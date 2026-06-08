import json

import requests
import stripe
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_http_methods

from .models import Order, OrderItem, Product
from .payments import (
    PaymentConfigurationError,
    capture_paypal_order,
    create_paypal_order,
    create_stripe_checkout_session,
    handle_paypal_webhook,
    handle_stripe_webhook,
)
from .services import send_contact_message, send_tracking_email


def _json_error(message: str, status: int = 400) -> JsonResponse:
    return JsonResponse({'error': message}, status=status)


def _parse_json(request):
    try:
        return json.loads(request.body), None
    except json.JSONDecodeError:
        return None, _json_error('Invalid JSON body')


def _serialize_product(request, product: Product) -> dict:
    image_url = None
    if product.image:
        image_url = request.build_absolute_uri(product.image.url)
    return {
        'id': product.pk,
        'name': product.name,
        'description': product.description,
        'price': str(product.price),
        'image_url': image_url,
        'created_at': product.created_at.isoformat(),
        'updated_at': product.updated_at.isoformat(),
    }


def _serialize_shipping(order: Order) -> dict:
    return {
        'line1': order.shipping_line1,
        'line2': order.shipping_line2,
        'city': order.shipping_city,
        'state': order.shipping_state,
        'postal_code': order.shipping_postal_code,
        'country': order.shipping_country,
    }


def _serialize_order_item(item: OrderItem) -> dict:
    return {
        'id': item.pk,
        'product_id': item.product_id,
        'product_name': item.product_name,
        'quantity': item.quantity,
        'unit_price': str(item.unit_price),
        'line_total': str(item.line_total),
    }


def _serialize_order_summary(order: Order) -> dict:
    return {
        'id': order.pk,
        'status': order.status,
        'customer_name': order.customer_name,
        'customer_email': order.customer_email,
        'total': str(order.total),
        'item_count': order.items.count(),
        'payment_provider': order.payment_provider or None,
        'paid_at': order.paid_at.isoformat() if order.paid_at else None,
        'is_paid': order.status == Order.Status.PAID,
        'tracking_number': order.tracking_number or None,
        'tracking_emailed_at': (
            order.tracking_emailed_at.isoformat()
            if order.tracking_emailed_at else None
        ),
        'created_at': order.created_at.isoformat(),
    }


def _serialize_order_detail(order: Order) -> dict:
    data = _serialize_order_summary(order)
    data.update({
        'shipping_address': _serialize_shipping(order),
        'items': [_serialize_order_item(item) for item in order.items.all()],
        'updated_at': order.updated_at.isoformat(),
    })
    return data


@require_GET
def health(request):
    return JsonResponse({
        'status': 'ok',
        'service': 'Samsonllc API',
    })


@require_GET
@ensure_csrf_cookie
def session(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'authenticated': False})
    return JsonResponse({
        'authenticated': True,
        'user': {
            'id': user.pk,
            'username': user.username,
        },
    })


@require_http_methods(['POST'])
def login_view(request):
    payload, error = _parse_json(request)
    if error:
        return error

    username = (payload.get('username') or '').strip()
    password = payload.get('password') or ''
    if not username or not password:
        return _json_error('Username and password are required')

    user = authenticate(request, username=username, password=password)
    if user is None:
        return _json_error('Invalid credentials', status=401)

    login(request, user)
    return JsonResponse({
        'authenticated': True,
        'user': {
            'id': user.pk,
            'username': user.username,
        },
    })


@require_http_methods(['POST'])
@login_required
def logout_view(request):
    logout(request)
    return JsonResponse({'authenticated': False})


@require_GET
def payment_config(request):
    from django.conf import settings
    return JsonResponse({
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY or None,
        'paypal_client_id': settings.PAYPAL_CLIENT_ID or None,
        'paypal_mode': settings.PAYPAL_MODE,
        'stripe_enabled': bool(settings.STRIPE_SECRET_KEY),
        'paypal_enabled': bool(
            settings.PAYPAL_CLIENT_ID and settings.PAYPAL_CLIENT_SECRET
        ),
    })


@require_GET
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related('items'), pk=pk)
    return JsonResponse({'order': _serialize_order_detail(order)})


@csrf_exempt
@require_http_methods(['POST'])
def order_pay_stripe(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related('items'), pk=pk)
    try:
        result = create_stripe_checkout_session(order)
    except PaymentConfigurationError as exc:
        return _json_error(str(exc), status=503)
    except ValueError as exc:
        return _json_error(str(exc))
    except stripe.error.StripeError as exc:
        return _json_error(f'Stripe error: {exc.user_message or exc}', status=502)
    if not result.get('checkout_url'):
        return _json_error('Stripe did not return a checkout URL.', status=502)
    return JsonResponse({
        'provider': 'stripe',
        'checkout_url': result['checkout_url'],
        'session_id': result['session_id'],
        'order_id': order.pk,
    })


@csrf_exempt
@require_http_methods(['POST'])
def order_pay_paypal(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related('items'), pk=pk)
    try:
        result = create_paypal_order(order)
    except PaymentConfigurationError as exc:
        return _json_error(str(exc), status=503)
    except ValueError as exc:
        return _json_error(str(exc))
    except requests.HTTPError as exc:
        return _json_error(f'PayPal error: {exc}', status=502)
    return JsonResponse({
        'provider': 'paypal',
        'approval_url': result['approval_url'],
        'paypal_order_id': result['paypal_order_id'],
        'order_id': order.pk,
    })


@csrf_exempt
@require_http_methods(['POST'])
def order_paypal_capture(request, pk):
    """Call after customer approves PayPal (return URL) if webhook is delayed."""
    order = get_object_or_404(Order.objects.prefetch_related('items'), pk=pk)
    try:
        order = capture_paypal_order(order)
    except PaymentConfigurationError as exc:
        return _json_error(str(exc), status=503)
    except ValueError as exc:
        return _json_error(str(exc))
    except requests.HTTPError as exc:
        return _json_error(f'PayPal capture failed: {exc}', status=502)
    return JsonResponse({'order': _serialize_order_detail(order)})


@csrf_exempt
@require_http_methods(['POST'])
def stripe_webhook(request):
    signature = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    try:
        order = handle_stripe_webhook(request.body, signature)
    except Exception as exc:
        return _json_error(str(exc), status=400)
    return JsonResponse({'received': True, 'order_id': order.pk if order else None})


@csrf_exempt
@require_http_methods(['POST'])
def paypal_webhook(request):
    payload, error = _parse_json(request)
    if error:
        return error
    try:
        order = handle_paypal_webhook(payload)
    except Exception as exc:
        return _json_error(str(exc), status=400)
    return JsonResponse({'received': True, 'order_id': order.pk if order else None})


@require_GET
def product_list(request):
    products = Product.objects.all()
    return JsonResponse({
        'products': [_serialize_product(request, product) for product in products],
    })


@csrf_exempt
@require_http_methods(['POST'])
def contact_submit(request):
    """Public contact form — sends to CONTACT_EMAIL."""
    payload, error = _parse_json(request)
    if error:
        return error

    name = (payload.get('name') or '').strip()
    email = (payload.get('email') or '').strip()
    message = (payload.get('message') or '').strip()

    if not name:
        return _json_error('Name is required')
    if not email:
        return _json_error('Email is required')
    if '@' not in email or len(email) > 254:
        return _json_error('Enter a valid email address')
    if not message:
        return _json_error('Message is required')
    if len(message) > 5000:
        return _json_error('Message is too long')

    try:
        send_contact_message(name, email, message)
    except Exception as exc:
        return _json_error(f'Could not send message: {exc}', status=502)

    return JsonResponse({'ok': True})


@csrf_exempt
@require_http_methods(['POST'])
def order_create(request):
    """Public checkout — customer frontend submits orders here."""
    payload, error = _parse_json(request)
    if error:
        return error

    customer_name = (payload.get('customer_name') or '').strip()
    customer_email = (payload.get('customer_email') or '').strip()
    shipping = payload.get('shipping_address') or {}
    items = payload.get('items') or []

    if not customer_name:
        return _json_error('customer_name is required')
    if not customer_email:
        return _json_error('customer_email is required')

    required_shipping = ('line1', 'city', 'state', 'postal_code')
    for field in required_shipping:
        if not (shipping.get(field) or '').strip():
            return _json_error(f'shipping_address.{field} is required')

    if not items:
        return _json_error('items must contain at least one product')

    with transaction.atomic():
        order = Order.objects.create(
            customer_name=customer_name,
            customer_email=customer_email,
            shipping_line1=shipping.get('line1', '').strip(),
            shipping_line2=(shipping.get('line2') or '').strip(),
            shipping_city=shipping.get('city', '').strip(),
            shipping_state=shipping.get('state', '').strip(),
            shipping_postal_code=shipping.get('postal_code', '').strip(),
            shipping_country=(shipping.get('country') or 'US').strip(),
            status=Order.Status.PENDING,
        )

        for entry in items:
            try:
                product_id = int(entry.get('product_id'))
                quantity = int(entry.get('quantity', 1))
            except (TypeError, ValueError):
                return _json_error('Each item needs product_id and quantity')

            if quantity < 1:
                return _json_error('quantity must be at least 1')

            product = Product.objects.filter(pk=product_id).first()
            if product is None:
                return _json_error(f'Product {product_id} not found', status=404)
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                quantity=quantity,
                unit_price=product.price,
            )

    order.refresh_from_db()
    return JsonResponse({'order': _serialize_order_detail(order)}, status=201)


@require_GET
@login_required
def admin_order_list(request):
    orders = Order.objects.prefetch_related('items').all()

    email_query = (request.GET.get('email') or '').strip()
    if email_query:
        orders = orders.filter(customer_email__icontains=email_query)

    status_filter = (request.GET.get('status') or '').strip()
    if status_filter:
        orders = orders.filter(status=status_filter)

    return JsonResponse({
        'orders': [_serialize_order_summary(order) for order in orders],
    })


@require_http_methods(['GET', 'PATCH'])
@login_required
def admin_order_detail(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related('items'), pk=pk)

    if request.method == 'GET':
        return JsonResponse({'order': _serialize_order_detail(order)})

    payload, error = _parse_json(request)
    if error:
        return error

    if 'status' in payload:
        status = payload['status']
        valid_statuses = {choice[0] for choice in Order.Status.choices}
        if status not in valid_statuses:
            return _json_error(f'status must be one of: {", ".join(sorted(valid_statuses))}')
        order.status = status

    if 'tracking_number' in payload:
        order.tracking_number = (payload['tracking_number'] or '').strip()

    order.save()
    return JsonResponse({'order': _serialize_order_detail(order)})


@require_http_methods(['POST'])
@login_required
def admin_order_send_tracking(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related('items'), pk=pk)
    payload, error = _parse_json(request)
    if error:
        return error

    if payload.get('tracking_number'):
        order.tracking_number = payload['tracking_number'].strip()
        order.save(update_fields=['tracking_number', 'updated_at'])

    if not order.tracking_number:
        return _json_error('tracking_number is required')

    try:
        send_tracking_email(order)
    except Exception as exc:
        return _json_error(f'Failed to send email: {exc}', status=500)

    if order.status == Order.Status.PAID:
        order.status = Order.Status.SHIPPED
        order.save(update_fields=['status', 'updated_at'])

    console_only = (
        settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend'
    )
    return JsonResponse({
        'sent': True,
        'delivered': not console_only,
        'warning': (
            'Email logged to server console only (SMTP not configured). '
            'Customer did not receive a message.'
            if console_only
            else None
        ),
        'to': order.customer_email,
        'order': _serialize_order_detail(order),
    })
