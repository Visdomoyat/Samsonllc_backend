# AWS S3 — product image storage

Render’s disk is **temporary**. Uploaded product photos must live in **Amazon S3** so they survive redeploys and load on your admin site and Netlify storefront.

When S3 is configured, new uploads go to:

```text
s3://your-bucket/media/products/<filename>
```

and are served at a public HTTPS URL.

---

## Part 1 — Create the S3 bucket

1. Sign in to [AWS Console](https://console.aws.amazon.com/) → **S3** → **Create bucket**.
2. **Bucket name:** e.g. `eliteforge-media` (must be globally unique).
3. **Region:** pick one close to your users (e.g. `us-east-2` Ohio). Note the region code.
4. **Block Public Access:** for simple public product images, **uncheck** “Block all public access” and confirm.  
   (Alternatively use CloudFront later; public bucket policy is the quickest start.)
5. Leave other defaults → **Create bucket**.

---

## Part 2 — Allow public read on uploaded images

1. Open your bucket → **Permissions** → **Bucket policy** → **Edit**.
2. Paste (replace `YOUR-BUCKET-NAME`):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadProductImages",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/media/*"
    }
  ]
}
```

3. **Save changes**.

Only objects under `media/` are public; the rest of the bucket stays private.

---

## Part 3 — CORS (for browser / Netlify)

Bucket → **Permissions** → **Cross-origin resource sharing (CORS)** → **Edit**:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedOrigins": [
      "https://eliteforge.netlify.app",
      "https://eliteforge-jkaf.onrender.com"
    ],
    "ExposeHeaders": [],
    "MaxAgeSeconds": 3000
  }
]
```

Adjust origins to your real Netlify and Render URLs.

---

## Part 4 — IAM user for Render

Do **not** use your root AWS account keys on Render.

1. **IAM** → **Users** → **Create user** (e.g. `eliteforge-render`).
2. **Attach policies directly** → **Create policy** → JSON:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::YOUR-BUCKET-NAME",
        "arn:aws:s3:::YOUR-BUCKET-NAME/media/*"
      ]
    }
  ]
}
```

3. Name the policy (e.g. `eliteforge-s3-media`) → create → attach to the user.
4. User → **Security credentials** → **Create access key** → **Application running outside AWS**.
5. Copy **Access key ID** and **Secret access key** (shown once).

---

## Part 5 — Environment variables on Render

Samsonllc web service → **Environment** → add:

| Key | Example |
|-----|---------|
| `AWS_ACCESS_KEY_ID` | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | `(secret)` |
| `AWS_STORAGE_BUCKET_NAME` | `eliteforge-media` |
| `AWS_S3_REGION_NAME` | `us-east-2` |
| `AWS_LOCATION` | `media` (optional, default) |

Redeploy after saving.

**Local `.env` (optional):** same variables if you want uploads to go to S3 while developing locally.

If `AWS_STORAGE_BUCKET_NAME` is **unset**, Django uses local `media/` (fine for local dev only).

---

## Part 6 — Verify

1. Redeploy on Render.
2. Log in → **Shop** → **Add product** with an image.
3. On the shop page, right‑click the product image → **Open image in new tab**.  
   URL should look like:

   ```text
   https://eliteforge-media.s3.us-east-2.amazonaws.com/media/products/photo.jpg
   ```

4. Netlify storefront: `GET /api/products/` should return the same `image_url`.

---

## Re-upload existing products

Images saved **before** S3 was enabled pointed at Render’s local disk. Those files are gone after redeploy. **Edit each product and upload the image again** once S3 is live.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Access Denied` on upload | IAM policy includes `PutObject` on `media/*` |
| Image URL 403 | Bucket policy allows `GetObject` on `media/*` |
| Wrong region | `AWS_S3_REGION_NAME` matches bucket region |
| App won’t start | All three: bucket name + access key + secret key set |
| Works locally, not Render | Env vars on Render, not only in local `.env` |

---

## Cost

S3 free tier includes modest storage and requests. Product photos for a small shop are usually a few cents per month.
