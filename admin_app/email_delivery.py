import logging

import requests
from django.conf import settings
from django.core.mail import EmailMessage, send_mail

logger = logging.getLogger(__name__)


def _send_via_sendgrid_api(
    *,
    subject: str,
    body: str,
    to_emails: list[str],
    from_email: str,
    reply_to: str | None = None,
) -> None:
    api_key = settings.SENDGRID_API_KEY
    if not api_key:
        raise RuntimeError('SENDGRID_API_KEY is not configured.')

    payload: dict = {
        'personalizations': [{'to': [{'email': email} for email in to_emails]}],
        'from': {'email': from_email},
        'subject': subject,
        'content': [{'type': 'text/plain', 'value': body}],
    }
    if reply_to:
        payload['reply_to'] = {'email': reply_to}

    response = requests.post(
        'https://api.sendgrid.com/v3/mail/send',
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        },
        json=payload,
        timeout=30,
    )
    if not response.ok:
        raise RuntimeError(
            f'SendGrid API error ({response.status_code}): {response.text[:500]}',
        )


def send_plain_email(
    *,
    subject: str,
    body: str,
    to_emails: list[str],
    from_email: str | None = None,
    reply_to: str | None = None,
) -> None:
    sender = from_email or settings.DEFAULT_FROM_EMAIL

    if settings.USE_SENDGRID_API:
        _send_via_sendgrid_api(
            subject=subject,
            body=body,
            to_emails=to_emails,
            from_email=sender,
            reply_to=reply_to,
        )
        return

    if reply_to:
        EmailMessage(
            subject=subject,
            body=body,
            from_email=sender,
            to=to_emails,
            reply_to=[reply_to],
        ).send(fail_silently=False)
        return

    send_mail(
        subject=subject,
        message=body,
        from_email=sender,
        recipient_list=to_emails,
        fail_silently=False,
    )
