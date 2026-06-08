import json
import logging
from decimal import Decimal

import requests
import stripe
from django.conf import settings
from django.utils import timezone

from .models import Order

logger = logging.getLogger(__name__)


class PaymentConfigurationError(Exception):
    pass


def _frontend_url(path: str) -> str:
    base = settings.FRONTEND_URL.rstrip('/')
    return f'{base}{path}'


def _order_must_be_payable(order: Order) -> None:
    if order.status == Order.Status.PAID:
        raise ValueError('Order is already paid.')
    if order.status == Order.Status.CANCELLED:
        raise ValueError('Order is cancelled.')
    if order.total <= 0:
        raise ValueError('Order total must be greater than zero.')


def stripe_checkout_blocks_paypal(order: Order) -> bool:
    """True while Stripe Checkout is still open or completing for this order."""
    if order.status != Order.Status.PENDING:
        return False
    if not order.stripe_checkout_session_id:
        return False
    if not settings.STRIPE_SECRET_KEY:
        return order.payment_provider == Order.PaymentProvider.STRIPE

    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        session = stripe.checkout.Session.retrieve(order.stripe_checkout_session_id)
    except stripe.error.StripeError:
        logger.warning(
            'Could not verify Stripe session %s for order %s',
            order.stripe_checkout_session_id,
            order.pk,
        )
        return order.payment_provider == Order.PaymentProvider.STRIPE

    return session.status in ('open', 'complete')


_PAYPAL_PENDING_STATUSES = frozenset({
    'CREATED',
    'SAVED',
    'APPROVED',
    'PAYER_ACTION_REQUIRED',
    'COMPLETED',
})


def _retrieve_paypal_order(paypal_order_id: str) -> dict | None:
    token = _paypal_access_token()
    response = requests.get(
        f'{_paypal_base_url()}/v2/checkout/orders/{paypal_order_id}',
        headers={'Authorization': f'Bearer {token}'},
        timeout=30,
    )
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


def _clear_paypal_checkout(order: Order) -> None:
    order.paypal_order_id = ''
    if order.payment_provider == Order.PaymentProvider.PAYPAL:
        order.payment_provider = ''
    order.save(update_fields=['paypal_order_id', 'payment_provider', 'updated_at'])


def paypal_checkout_blocks_stripe(order: Order) -> bool:
    """True while PayPal Checkout is still open or completing for this order."""
    if order.status != Order.Status.PENDING:
        return False
    if not order.paypal_order_id:
        return False
    if not settings.PAYPAL_CLIENT_ID or not settings.PAYPAL_CLIENT_SECRET:
        return order.payment_provider == Order.PaymentProvider.PAYPAL

    try:
        data = _retrieve_paypal_order(order.paypal_order_id)
    except (PaymentConfigurationError, requests.HTTPError):
        logger.warning(
            'Could not verify PayPal order %s for order %s',
            order.paypal_order_id,
            order.pk,
        )
        return order.payment_provider == Order.PaymentProvider.PAYPAL

    if data is None:
        return False

    return data.get('status') in _PAYPAL_PENDING_STATUSES


def release_paypal_checkout(order: Order) -> bool:
    """Release an abandoned PayPal Checkout so card payment can be used."""
    if not order.paypal_order_id:
        return False

    try:
        data = _retrieve_paypal_order(order.paypal_order_id)
    except (PaymentConfigurationError, requests.HTTPError):
        logger.warning(
            'Could not release PayPal order %s for order %s',
            order.paypal_order_id,
            order.pk,
        )
        return False

    if data is None:
        _clear_paypal_checkout(order)
        return True

    status = data.get('status', '')
    if status == 'VOIDED':
        return False

    if status == 'APPROVED':
        token = _paypal_access_token()
        response = requests.post(
            f'{_paypal_base_url()}/v2/checkout/orders/{order.paypal_order_id}/void',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
            },
            timeout=30,
        )
        if response.ok:
            return True

    if status in ('CREATED', 'SAVED', 'PAYER_ACTION_REQUIRED'):
        _clear_paypal_checkout(order)
        return True

    return False


def release_stripe_checkout(order: Order) -> bool:
    """Expire an open Stripe Checkout session so PayPal can be used."""
    if not order.stripe_checkout_session_id or not settings.STRIPE_SECRET_KEY:
        return False

    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        session = stripe.checkout.Session.retrieve(order.stripe_checkout_session_id)
    except stripe.error.StripeError:
        logger.warning(
            'Could not release Stripe session %s for order %s',
            order.stripe_checkout_session_id,
            order.pk,
        )
        return False

    if session.status != 'open':
        return False

    stripe.checkout.Session.expire(order.stripe_checkout_session_id)
    return True


def mark_order_paid(order: Order, provider: str, **extra_fields) -> Order:
    if order.status == Order.Status.PAID:
        return order

    order.status = Order.Status.PAID
    order.payment_provider = provider
    order.paid_at = timezone.now()
    for field, value in extra_fields.items():
        setattr(order, field, value)
    order.save()
    return order


def create_stripe_checkout_session(order: Order) -> dict:
    if not settings.STRIPE_SECRET_KEY:
        raise PaymentConfigurationError('STRIPE_SECRET_KEY is not configured.')

    _order_must_be_payable(order)
    if paypal_checkout_blocks_stripe(order):
        raise ValueError(
            'PayPal checkout is in progress for this order. '
            'Complete or cancel PayPal payment before using card checkout.',
        )
    stripe.api_key = settings.STRIPE_SECRET_KEY

    if order.stripe_checkout_session_id:
        try:
            existing = stripe.checkout.Session.retrieve(
                order.stripe_checkout_session_id,
            )
            if existing.status == 'open' and existing.url:
                return {
                    'checkout_url': existing.url,
                    'session_id': existing.id,
                }
        except stripe.error.StripeError:
            logger.warning(
                'Could not reuse Stripe session %s for order %s',
                order.stripe_checkout_session_id,
                order.pk,
            )

    line_items = []
    for item in order.items.all():
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(item.unit_price * 100),
                'product_data': {
                    'name': item.product_name,
                },
            },
            'quantity': item.quantity,
        })

    session = stripe.checkout.Session.create(
        mode='payment',
        customer_email=order.customer_email,
        line_items=line_items,
        metadata={'order_id': str(order.pk)},
        success_url=_frontend_url(
            f'/checkout/success?order_id={order.pk}'
            '&session_id={CHECKOUT_SESSION_ID}',
        ),
        cancel_url=_frontend_url(f'/checkout/cancel?order_id={order.pk}'),
    )

    order.stripe_checkout_session_id = session.id
    order.payment_provider = Order.PaymentProvider.STRIPE
    order.save(update_fields=['stripe_checkout_session_id', 'payment_provider', 'updated_at'])

    return {
        'checkout_url': session.url,
        'session_id': session.id,
    }


def _paypal_base_url() -> str:
    if settings.PAYPAL_MODE == 'live':
        return 'https://api-m.paypal.com'
    return 'https://api-m.sandbox.paypal.com'


def _paypal_access_token() -> str:
    if not settings.PAYPAL_CLIENT_ID or not settings.PAYPAL_CLIENT_SECRET:
        raise PaymentConfigurationError('PayPal credentials are not configured.')

    response = requests.post(
        f'{_paypal_base_url()}/v1/oauth2/token',
        data={'grant_type': 'client_credentials'},
        auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()['access_token']


def create_paypal_order(order: Order) -> dict:
    _order_must_be_payable(order)
    if stripe_checkout_blocks_paypal(order):
        raise ValueError(
            'Card checkout is in progress for this order. '
            'Complete or cancel Stripe payment before using PayPal.',
        )
    token = _paypal_access_token()

    total = format(order.total, '.2f')
    payload = {
        'intent': 'CAPTURE',
        'purchase_units': [{
            'reference_id': str(order.pk),
            'amount': {
                'currency_code': 'USD',
                'value': total,
            },
            'description': f'Samson LLC order #{order.pk}',
        }],
        'application_context': {
            'brand_name': 'Samson LLC',
            'user_action': 'PAY_NOW',
            'return_url': _frontend_url(f'/checkout/success?order_id={order.pk}'),
            'cancel_url': _frontend_url(f'/checkout/cancel?order_id={order.pk}'),
        },
    }

    response = requests.post(
        f'{_paypal_base_url()}/v2/checkout/orders',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        },
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    approval_url = None
    for link in data.get('links', []):
        if link.get('rel') == 'approve':
            approval_url = link.get('href')
            break

    if not approval_url:
        raise PaymentConfigurationError('PayPal approval URL was not returned.')

    order.paypal_order_id = data['id']
    order.payment_provider = Order.PaymentProvider.PAYPAL
    order.save(update_fields=['paypal_order_id', 'payment_provider', 'updated_at'])

    return {
        'approval_url': approval_url,
        'paypal_order_id': data['id'],
    }


def capture_paypal_order(order: Order) -> Order:
    if not order.paypal_order_id:
        raise ValueError('No PayPal order id on this order.')

    if order.status == Order.Status.PAID:
        return order

    token = _paypal_access_token()
    response = requests.post(
        f'{_paypal_base_url()}/v2/checkout/orders/{order.paypal_order_id}/capture',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    if data.get('status') != 'COMPLETED':
        raise ValueError(f'PayPal capture status: {data.get("status")}')

    return mark_order_paid(order, Order.PaymentProvider.PAYPAL)


def handle_stripe_webhook(payload: bytes, signature: str) -> Order | None:
    if not settings.STRIPE_WEBHOOK_SECRET:
        logger.warning('STRIPE_WEBHOOK_SECRET not set; skipping Stripe webhook verification.')
        event = json.loads(payload)
    else:
        event = stripe.Webhook.construct_event(
            payload, signature, settings.STRIPE_WEBHOOK_SECRET,
        )

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session.get('metadata', {}).get('order_id')
        if not order_id:
            return None
        order = Order.objects.filter(pk=order_id).first()
        if order:
            mark_order_paid(
                order,
                Order.PaymentProvider.STRIPE,
                stripe_checkout_session_id=session.get('id', ''),
            )
            return order
    return None


def handle_paypal_webhook(payload: dict) -> Order | None:
    event_type = payload.get('event_type')
    resource = payload.get('resource', {})

    if event_type == 'CHECKOUT.ORDER.APPROVED':
        paypal_order_id = resource.get('id')
        order = Order.objects.filter(paypal_order_id=paypal_order_id).first()
        if order and order.status != Order.Status.PAID:
            return capture_paypal_order(order)

    if event_type == 'PAYMENT.CAPTURE.COMPLETED':
        paypal_order_id = resource.get('supplementary_data', {}).get(
            'related_ids', {},
        ).get('order_id')
        if not paypal_order_id:
            return None
        order = Order.objects.filter(paypal_order_id=paypal_order_id).first()
        if order and order.status != Order.Status.PAID:
            return mark_order_paid(order, Order.PaymentProvider.PAYPAL)

    return None
