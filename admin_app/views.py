from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductForm
from .models import Product


@login_required
def landing(request):
    return render(request, 'landing.html')


@login_required
def search(request):
    query = request.GET.get('q', '').strip()
    return render(request, 'landing.html', {'search_query': query})


@login_required
def shop(request):
    products = Product.objects.all()
    return render(request, 'shop.html', {'products': products})


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
    return render(request, 'landing.html')


@login_required
def transactions(request):
    return render(request, 'landing.html')
