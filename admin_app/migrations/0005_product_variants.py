from decimal import Decimal

from django.db import migrations, models
import django.db.models.deletion


def create_variants_from_product_prices(apps, schema_editor):
    Product = apps.get_model('admin_app', 'Product')
    ProductVariant = apps.get_model('admin_app', 'ProductVariant')
    for product in Product.objects.all():
        price = getattr(product, 'price', None)
        if price is None:
            continue
        ProductVariant.objects.create(
            product_id=product.pk,
            size_value=Decimal('1'),
            size_unit='mg',
            price=price,
            is_active=True,
            display_order=0,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0004_stack_blend'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductVariant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size_value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('size_unit', models.CharField(choices=[('mg', 'MG'), ('ml', 'ML')], max_length=2)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_active', models.BooleanField(default=True, help_text='Inactive variants are hidden from the storefront.')),
                ('display_order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='admin_app.product')),
            ],
            options={
                'ordering': ['display_order', 'size_value', 'id'],
            },
        ),
        migrations.AddConstraint(
            model_name='productvariant',
            constraint=models.UniqueConstraint(fields=('product', 'size_value', 'size_unit'), name='unique_product_size'),
        ),
        migrations.RunPython(
            create_variants_from_product_prices,
            migrations.RunPython.noop,
        ),
        migrations.RemoveField(
            model_name='product',
            name='price',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product_description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product_variant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_items', to='admin_app.productvariant'),
        ),
    ]
