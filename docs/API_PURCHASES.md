# Purchases API — Frontend integration

Base URL: `http://127.0.0.1:8000/api`

Admin requests: `credentials: 'include'` and CSRF header from cookie after `GET /api/auth/session/`.

## Customer checkout (public)

### `POST /api/orders/`

```json
{
  "customer_name": "Jane Doe",
  "customer_email": "jane@example.com",
  "shipping_address": {
    "line1": "123 Main St",
    "line2": "",
    "city": "Boston",
    "state": "MA",
    "postal_code": "02101",
    "country": "US"
  },
  "items": [
    { "product_id": 1, "quantity": 2 }
  ]
}
```

Response `201`: `{ "order": { ...full order... } }`

## Admin — purchased orders

### `GET /api/admin/orders/`

Query: `?email=` `?status=paid`

### `GET /api/admin/orders/<id>/`

### `PATCH /api/admin/orders/<id>/`

```json
{
  "status": "shipped",
  "tracking_number": "1Z999AA10123456784"
}
```

### `POST /api/admin/orders/<id>/send-tracking/`

```json
{ "tracking_number": "1Z999AA10123456784" }
```

Sends email to `customer_email`. Sets `tracking_emailed_at`. In dev, email prints to the Django console.

## Auth

- `POST /api/auth/login/`
- `GET /api/auth/session/`
- `POST /api/auth/logout/`

## Products (catalog)

- `GET /api/products/`
