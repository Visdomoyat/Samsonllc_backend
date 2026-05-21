from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Order


def send_tracking_email(order: Order) -> None:
    if not order.tracking_number:
        raise ValueError('Tracking number is required before sending email.')

    subject = f'Eliteforge — Tracking for order #{order.pk}'
    message = (
        f'Hello {order.customer_name},\n\n'
        f'Your order #{order.pk} has shipped.\n\n'
        f'Tracking number: {order.tracking_number}\n\n'
        f'Shipping address:\n'
        f'{order.shipping_line1}\n'
    )
    if order.shipping_line2:
        message += f'{order.shipping_line2}\n'
    message += (
        f'{order.shipping_city}, {order.shipping_state} '
        f'{order.shipping_postal_code}\n'
        f'{order.shipping_country}\n\n'
        f'Thank you for your order.\n'
        f'Eliteforge'
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.customer_email],
        fail_silently=False,
    )
    order.tracking_emailed_at = timezone.now()
    order.save(update_fields=['tracking_emailed_at', 'updated_at'])
