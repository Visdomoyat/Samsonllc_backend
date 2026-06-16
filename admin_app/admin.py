from django.contrib import admin

from .models import Order, OrderItem, Product, ProductVariant, StackBlend


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('size_value', 'size_unit', 'price', 'is_active', 'display_order')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'variant_count', 'created_at')
    search_fields = ('name',)
    inlines = [ProductVariantInline]

    @admin.display(description='Sizes')
    def variant_count(self, obj):
        return obj.variants.count()


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size_label', 'price', 'is_active', 'display_order')
    list_filter = ('size_unit', 'is_active')
    search_fields = ('product__name',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'quantity', 'unit_price')


@admin.register(StackBlend)
class StackBlendAdmin(admin.ModelAdmin):
    list_display = ('name', 'kind', 'price', 'is_active', 'display_order', 'created_at')
    list_filter = ('kind', 'is_active')
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
