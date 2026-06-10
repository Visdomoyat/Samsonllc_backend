from django.contrib import admin

from .models import Order, OrderItem, Product, StackBlend


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'quantity', 'unit_price')


@admin.register(StackBlend)
class StackBlendAdmin(admin.ModelAdmin):
    list_display = ('name', 'kind', 'price', 'is_active', 'display_order', 'created_at')
    list_filter = ('kind', 'is_active')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'created_at')
    search_fields = ('name',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer_name',
        'customer_email',
        'status',
        'tracking_number',
        'created_at',
    )
    list_filter = ('status',)
    search_fields = ('customer_name', 'customer_email', 'tracking_number')
    inlines = [OrderItemInline]
    readonly_fields = (
        'payment_provider',
        'stripe_checkout_session_id',
        'paypal_order_id',
        'paid_at',
        'tracking_emailed_at',
        'created_at',
        'updated_at',
    )
