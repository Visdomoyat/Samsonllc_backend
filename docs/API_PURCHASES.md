# Purchases & payments API

Base URL: `http://127.0.0.1:8000/api`

Set keys in environment (see `.env.example`). Load with `export $(cat .env | xargs)` or pipenv `--env`.

## Payment config (frontend)

### `GET /api/config/payments/`

```json
{
  "stripe_publishable_key": "pk_test_...",
  "paypal_client_id": "...",
  "paypal_mode": "sandbox",
  "stripe_enabled": true,
  "paypal_enabled": true
}
```

## Checkout flow

### 1. `POST /api/orders/` — create order (`status: pending`)

Same body as before (customer, shipping, items).

### 2a. Pay with Stripe — `POST /api/orders/<id>/pay/stripe/`

```json
{
  "checkout_url": "https://checkout.stripe.com/...",
  "session_id": "cs_...",
  "order_id": 12
}
```

Redirect customer to `checkout_url`. On success, Stripe webhook marks order **paid**.

### 2b. Pay with PayPal — `POST /api/orders/<id>/pay/paypal/`

```json
{
  "approval_url": "https://www.sandbox.paypal.com/...",
  "paypal_order_id": "...",
  "order_id": 12
}
```

Redirect to `approval_url`. After approval:

- Webhook captures payment, **or**
- `POST /api/orders/<id>/paypal/capture/` from your success page

### 3. `GET /api/orders/<id>/` — order status (thank-you page)

## Webhooks (backend only)

| URL | Provider |
|-----|----------|
| `POST /api/webhooks/stripe/` | Stripe `checkout.session.completed` |
| `POST /api/webhooks/paypal/` | PayPal `CHECKOUT.ORDER.APPROVED`, `PAYMENT.CAPTURE.COMPLETED` |

**Stripe local testing:**

```bash
stripe listen --forward-to localhost:8000/api/webhooks/stripe/
```

Use the printed `whsec_...` as `STRIPE_WEBHOOK_SECRET`.

**PayPal:** Register webhook URL in PayPal Developer Dashboard → your ngrok/public URL + `/api/webhooks/paypal/`.

## Admin (paid orders)

`GET /api/admin/orders/?status=paid` — requires admin session (`credentials: 'include'`).

Includes `payment_provider`, `paid_at`, `is_paid`.

## Frontend summary

```
1. POST /api/orders/           → order id
2. POST /api/orders/:id/pay/stripe/  OR  pay/paypal/
3. Redirect to checkout_url / approval_url
4. Success page: GET /api/orders/:id/  (+ POST paypal/capture for PayPal if needed)
```

Admin Purchased tab: only show `status=paid` (or filter tabs).
