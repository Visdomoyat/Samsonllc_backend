from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductForm
from .models import Order, Product
from .services import send_tracking_email


@login_required
def landing(request):
    return render(request, 'landing.html')


@login_required
def search(request):
    query = request.GET.get('q', '').strip()
    return render(request, 'landing.html', {'search_query': query})


@login_required
def shop(request):
    products = list(Product.objects.all())
    product_rows = [
        products[i:i + 4] for i in range(0, len(products), 4)
    ]
    return render(request, 'shop.html', {
        'products': products,
        'product_rows': product_rows,
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
            messages.success(request, f'Tracking email sent to {order.customer_email}.')
        except Exception as exc:
            messages.error(request, f'Failed to send email: {exc}')
    return redirect('purchased')


@login_required
def transactions(request):
    return render(request, 'landing.html')
