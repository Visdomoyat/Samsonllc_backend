# Eliteforge — Website Guide

Welcome! This guide explains how to use your **admin website** to manage products and customer orders. Your customers shop on your public storefront (Eliteforge on Netlify); you manage everything from your secure admin login.

---

## Getting started

### How to log in

1. Open your admin website in a browser (your team will provide the link).
2. Enter your **username** and **password**.
3. Click **Sign in**.

After signing in, you’ll land on the **Shop** page.

### How to log out

Click **Logout** in the top navigation (on phones, open the **menu ☰** first).

---

## Your admin dashboard at a glance

Once logged in, you’ll see a header with:

| Area | What it’s for |
|------|----------------|
| **Logo** | Click to return to Shop |
| **Search bar** | Find products by name or description |
| **Shop** | Add and manage products |
| **Purchased** | View and fulfill customer orders |
| **Account** | Change username or password |
| **Logout** | Sign out securely |

---

## Managing products (Shop)

The **Shop** page is your product catalog—the items customers can buy on your storefront.

### View products

All products appear in a grid with photo, name, description, and price.

### Search for a product

Use the search bar at the top. Type a product name or keyword and press **Search**.

### Add a new product

1. Click **Add product**.
2. Fill in:
   - **Product name**
   - **Image** (upload a photo from your computer)
   - **Description**
   - **Price**
3. Click **Save product**.

You’ll return to Shop and see the new item listed.

### Edit a product

1. On the Shop page, find the product.
2. Click **Edit**.
3. Change any fields. To keep the current photo, leave **Image** blank.
4. Click **Save product**.

### Delete a product

1. Click **Delete** on the product card.
2. Confirm when prompted.

The product will be removed from your catalog and will no longer appear on the customer storefront.

---

## Managing orders (Purchased)

The **Purchased** page shows orders placed by customers through your online store.

### Find orders

**Filter by status** — use the tabs at the top:

| Status | Meaning |
|--------|---------|
| **All** | Every order |
| **Pending** | Order placed; payment not completed yet |
| **Paid** | Payment received — ready to fulfill |
| **Shipped** | Order sent; tracking may have been emailed |
| **Delivered** | Order completed |
| **Cancelled** | Order was cancelled |

**Search by email** — enter a customer’s email and click **Search** to find their orders.

### What you see on each order

Each order shows:

- Order number and date  
- Customer name and email  
- Shipping address  
- Products ordered, quantities, and total  
- Payment method and date paid (when applicable)  

### Update an order

At the bottom of each order card:

1. **Status** — choose the correct stage from the dropdown.  
2. **Tracking #** — enter the carrier tracking number when you ship.  
3. Click **Save**.

### Email tracking to the customer

After you save a tracking number:

1. Click **Email tracking to customer**.  
2. Confirm when asked.

The customer receives an email with their tracking number. If the order was **Paid**, the status may automatically move to **Shipped**.

> **Note:** The tracking button stays disabled until a tracking number is saved.

---

## Account settings

Click **Account** in the top navigation to update your login details.

### Change username

1. Open **Account**.
2. Enter your new username.
3. Click **Save username**.

### Change password

1. Open **Account**.
2. Enter your **current password**.
3. Enter and confirm your **new password**.
4. Click **Change password**.

You stay signed in after updating your password.

---

## Typical daily workflow

```
1. Log in
2. Shop → add or update products as needed
3. Purchased → open "Paid" orders
4. Pack and ship the order
5. Enter tracking number → Save
6. Email tracking to customer
7. Log out when finished
```

---

## What your customers see (storefront)

Customers do **not** use your admin login. They shop on your public website (Eliteforge on Netlify):

1. Browse products  
2. Add items to cart and check out  
3. Pay with card (Stripe) or PayPal  
4. Receive confirmation and, later, a tracking email from you  

New orders appear in your **Purchased** section—usually under **Pending** first, then **Paid** after successful payment.

---

## Tips & reminders

- **Product photos** — Use clear, well-lit images. Upload JPG or PNG files when adding or editing a product.  
- **Paid before shipping** — Confirm payment status is **Paid** before shipping.  
- **Tracking** — Always save the tracking number before sending the tracking email.  
- **Stay signed in** — For security, log out when you’re done, especially on shared computers.  
- **Need help?** — Contact your developer if you can’t log in, images won’t upload, or orders aren’t appearing.

---

## Quick reference

| I want to… | Go to… |
|------------|--------|
| Sign in | Admin website home page |
| Add or edit products | **Shop** |
| See customer orders | **Purchased** |
| Ship an order | **Purchased** → tracking # → **Save** → **Email tracking** |
| Change login details | **Account** |
| Sign out | **Logout** |

---

*Eliteforge / Samson LLC — Admin website guide*
