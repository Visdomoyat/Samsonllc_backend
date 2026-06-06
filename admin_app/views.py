from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AccountPasswordChangeForm, ProductForm, UsernameChangeForm
from .models import Order, Product
from .services import send_tracking_email



@login_required
def shop(request):
    query = (request.GET.get('q') or '').strip()
    products = list(Product.objects.all())
    if query:
        products = [
            p for p in products
            if query.lower() in p.name.lower()
            or query.lower() in (p.description or '').lower()
        ]
    product_rows = [
        products[i:i + 4] for i in range(0, len(products), 4)
    ]
    return render(request, 'shop.html', {
        'products': products,
        'product_rows': product_rows,
        'search_query': query,
    })


@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully.')
            return redirect('shop')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {
        'form': form,
        'page_title': 'Add product',
    })


@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('shop')
    else:
        form = ProductForm(instance=product)
    return render(request, 'product_form.html', {
        'form': form,
        'product': product,
        'page_title': 'Edit product',
    })


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        if product.image:
            product.image.delete(save=False)
        product.delete()
        messages.success(request, 'Product deleted successfully.')
    return redirect('shop')


@login_required
def purchased(request):
    orders = Order.objects.prefetch_related('items').all()
    status_filter = (request.GET.get('status') or '').strip()
    if status_filter:
        orders = orders.filter(status=status_filter)
    email_filter = (request.GET.get('email') or '').strip()
    if email_filter:
        orders = orders.filter(customer_email__icontains=email_filter)
    return render(request, 'purchased.html', {
        'orders': orders,
        'status_filter': status_filter,
        'email_filter': email_filter,
        'status_choices': Order.Status.choices,
    })


@login_required
def purchased_order_update(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        status = (request.POST.get('status') or '').strip()
        if status in dict(Order.Status.choices):
            order.status = status
        order.tracking_number = (request.POST.get('tracking_number') or '').strip()
        order.save()
        messages.success(request, f'Order #{order.pk} updated.')
    return redirect('purchased')


@login_required
def purchased_send_tracking(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        tracking = (request.POST.get('tracking_number') or '').strip()
        if tracking:
            order.tracking_number = tracking
            order.save(update_fields=['tracking_number', 'updated_at'])
        if not order.tracking_number:
            messages.error(request, 'Tracking number is required.')
            return redirect('purchased')
        try:
            send_tracking_email(order)
            if order.status == Order.Status.PAID:
                order.status = Order.Status.SHIPPED
                order.save(update_fields=['status', 'updated_at'])
            if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
                messages.warning(
                    request,
                    f'Email logged to server console only (SMTP not configured). '
                    f'{order.customer_email} did not receive a message.',
                )
            else:
                messages.success(request, f'Tracking email sent to {order.customer_email}.')
        except Exception as exc:
            messages.error(request, f'Failed to send email: {exc}')
    return redirect('purchased')


@login_required
def transactions(request):
    return render(request, 'landing.html')


@login_required
def account_settings(request):
    username_form = UsernameChangeForm(instance=request.user)
    password_form = AccountPasswordChangeForm(user=request.user)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'username':
            username_form = UsernameChangeForm(request.POST, instance=request.user)
            if username_form.is_valid():
                username_form.save()
                messages.success(request, 'Username updated successfully.')
                return redirect('account_settings')
            messages.error(request, 'Please fix the errors below.')

        elif form_type == 'password':
            password_form = AccountPasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password updated successfully.')
                return redirect('account_settings')
            messages.error(request, 'Please fix the errors below.')

    return render(request, 'account_settings.html', {
        'username_form': username_form,
        'password_form': password_form,
    })
