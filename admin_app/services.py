from django.conf import settings
from django.utils import timezone

from .email_delivery import send_plain_email
from .models import Order


def ensure_email_can_deliver() -> None:
    """Console backend only prints to logs — customers never receive mail."""
    if settings.USE_SENDGRID_API and settings.SENDGRID_API_KEY:
        return
    if settings.EMAIL_BACKEND == "django.core.mail.backends.console.EmailBackend":
        if settings.DEBUG:
            return
        raise RuntimeError(
            "Email is not configured for production. Set SENDGRID_API_KEY "
            "(or EMAIL_HOST_PASSWORD with an SG key) and USE_SENDGRID_API=True "
            "on Render free tier, or configure SMTP on a paid instance."
        )
    if not settings.EMAIL_HOST:
        raise RuntimeError("EMAIL_HOST is not configured.")


def send_order_confirmation_email(order: Order) -> None:
    ensure_email_can_deliver()

    lines = [
        f'Hello {order.customer_name},',
        '',
        f'Thank you for your order. Payment has been received.',
        '',
        f'Order #{order.pk}',
        f'Total: ${order.total:.2f}',
        '',
        'Items:',
    ]
    for item in order.items.all():
        lines.append(
            f'  - {item.product_name} x{item.quantity}  ${item.line_total:.2f}',
        )
    lines.extend([
        '',
        'Shipping to:',
        order.shipping_line1,
    ])
    if order.shipping_line2:
        lines.append(order.shipping_line2)
    lines.extend([
        f'{order.shipping_city}, {order.shipping_state} {order.shipping_postal_code}',
        order.shipping_country,
        '',
        'We will email you tracking information when your order ships.',
        '',
        'Thank you,',
        'Eliteforge Peptide',
    ])

    send_plain_email(
        subject=f'Eliteforge — Order #{order.pk} confirmed',
        body='\n'.join(lines),
        to_emails=[order.customer_email],
    )


def send_tracking_email(order: Order) -> None:
    if not order.tracking_number:
        raise ValueError('Tracking number is required before sending email.')

    ensure_email_can_deliver()

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

    send_plain_email(
        subject=subject,
        body=message,
        to_emails=[order.customer_email],
    )
    order.tracking_emailed_at = timezone.now()
    order.save(update_fields=['tracking_emailed_at', 'updated_at'])


def send_contact_message(name: str, email: str, message: str) -> None:
    ensure_email_can_deliver()

    subject = f'Eliteforge contact — {name}'
    body = (
        f'New message from the Eliteforge contact form.\n\n'
        f'Name: {name}\n'
        f'Email: {email}\n\n'
        f'Message:\n{message}\n'
    )

    send_plain_email(
        subject=subject,
        body=body,
        to_emails=[settings.CONTACT_EMAIL],
        reply_to=email,
    )
