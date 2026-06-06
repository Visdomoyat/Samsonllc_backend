# Eliteforge / Samson LLC — Site Navigation Guide

This project has **two surfaces**:

| Surface | Who uses it | Where it lives |
|---------|-------------|----------------|
| **Admin website** | Staff (you) | Django on Render, e.g. `https://eliteforge-jkaf.onrender.com` |
| **Customer storefront** | Shoppers | Netlify frontend, e.g. `https://eliteforge.netlify.app` (calls the API) |

---

## Admin website (staff)

All admin pages require login except the sign-in page itself.

### 1. Sign in

| | |
|--|--|
| **URL** | `/` |
| **What you do** | Enter username and password → **Sign in** |
| **After login** | Redirects to **Shop** |

Create a user locally or on Render:

```bash
pipenv run python manage.py createsuperuser
```

On Render you can also set `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_PASSWORD`, and `DJANGO_SUPERUSER_EMAIL` so `build.sh` creates one on deploy.

---

### 2. Header navigation (logged in)

After login, the top bar includes:

| Link / control | Goes to | Purpose |
|----------------|---------|---------|
| **Logo** | Shop | Home for admin |
| **Search** | Shop (filtered) | Search products by name or description |
| **Shop** | `/shop/` | Manage products |
| **Purchased** | `/purchased/` | View and fulfill customer orders |
| **Logout** | Sign out → login page | Ends your session |

On mobile, open the **menu (☰)** button to reach Shop, Purchased, and Logout.

---

### 3. Shop — product catalog (admin)

**URL:** `/shop/`

| Action | How |
|--------|-----|
| **View products** | Grid of all products with image, description, price |
| **Search** | Use the header search box (same as Shop page `?q=...`) |
| **Add product** | Click **Add product** → fill name, image, description, price → **Save product** |
| **Edit product** | Click **Edit** on a product card |
| **Delete product** | Click **Delete** → confirm |

**URLs:**

| Page | URL |
|------|-----|
| Shop list | `/shop/` |
| Add product | `/shop/add/` |
| Edit product | `/shop/<id>/edit/` |

Product images are uploaded files stored under `/media/products/` (separate from the site logo in `/static/`).

---

### 4. Purchased — order management

**URL:** `/purchased/`

Customer orders from the Netlify storefront appear here after checkout.

#### Filter orders

| Control | Purpose |
|---------|---------|
| **Status tabs** | All · Pending · Paid · Shipped · Delivered · Cancelled |
| **Search by email** | Find orders for a specific customer |

#### Work on an order

Each order card shows:

- Customer name and email  
- Shipping address  
- Line items and total  
- Payment provider and paid time (when applicable)

| Action | How |
|--------|-----|
| **Update status** | Choose status in dropdown → **Save** |
| **Add tracking #** | Enter tracking number → **Save** |
| **Email tracking** | After tracking is saved → **Email tracking to customer** (marks shipped if order was paid) |

**Order status flow (typical):**

```
pending → paid → shipped → delivered
                    ↘ cancelled (if needed)
```

---

### 5. Django admin (optional)

**URL:** `/admin/`

Full Django admin for users, products, orders, and raw database records. Same superuser account as the main login.

---

### 6. Transactions page

**URL:** `/transactions/`

Placeholder route in the app; use **Purchased** for order work unless this page is built out further.

---

## Customer storefront (Netlify + API)

Shoppers use the **Netlify site**, not the Django HTML pages. The frontend talks to the backend API.

**API base:** `https://<your-render-app>.onrender.com/api`

### Typical shopper journey

```
Browse products     →  GET  /api/products/
Add to cart / checkout
Create order        →  POST /api/orders/
Pay (Stripe/PayPal) →  POST /api/orders/<id>/pay/stripe/  or  .../pay/paypal/
Redirect to payment provider
Return to Netlify   →  /checkout/success?order_id=...
Confirm order       →  GET  /api/orders/<id>/
```

Payment keys for the frontend: `GET /api/config/payments/`

Full API details: [API_PURCHASES.md](./API_PURCHASES.md)

---

## Quick URL reference (admin site)

| Path | Page |
|------|------|
| `/` | Login |
| `/shop/` | Product list |
| `/shop/add/` | Add product |
| `/shop/<id>/edit/` | Edit product |
| `/purchased/` | Orders |
| `/logout/` | Log out (POST) |
| `/admin/` | Django admin |
| `/api/health/` | API health check (JSON) |

---

## Environment URLs

Set these so checkout redirects and CORS work:

| Variable | Example | Used for |
|----------|---------|----------|
| `FRONTEND_URL` (Render) | `https://eliteforge.netlify.app` | Stripe/PayPal return URLs |
| `VITE_API_URL` (Netlify) | `https://eliteforge-jkaf.onrender.com/api` | Frontend API calls |

---

## Troubleshooting

| Problem | Check |
|---------|--------|
| Can't log in | User exists? `createsuperuser` · migrations run? |
| No CSS/logo | `collectstatic` on deploy · Start command `./start.sh` |
| Product image missing | `/media/products/...` loads? Re-upload after deploy |
| No orders in Purchased | Customer completed checkout on Netlify? Filter **Paid** |
| Netlify can't reach API | CORS · `VITE_API_URL` · Render service live |
