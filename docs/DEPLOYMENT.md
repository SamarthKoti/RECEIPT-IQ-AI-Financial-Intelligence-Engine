# Free demo deployment: Render + Supabase

The Docker image builds React, installs Tesseract, and serves the frontend and API on one HTTPS origin. Render's free filesystem is ephemeral; PostgreSQL and a private Supabase Storage bucket persist records and normalized receipt images separately. Local development keeps using SQLite and the upload folder.

## Hosting configuration

- Render: Docker web service, **Free**, Singapore, one instance/worker, health path `/api/health`. Root `Dockerfile`; no build/start command overrides. `render.yaml` records the configuration.
- Supabase: free project in Singapore. Create a **private** `receipts` bucket; allow `image/png`. Do not add anonymous read/write policies. The backend checks bucket privacy before starting.
- `DATABASE_URL`: `postgresql+psycopg://USER:PASSWORD@SESSION_POOLER_HOST:5432/postgres?sslmode=require`. Use Supabase's IPv4-compatible **session pooler**, not the transaction pooler. URL-encode credentials. Use a dedicated backend database role with table-creation rights in public, or the dashboard's server connection role.
- `SUPABASE_URL`: project HTTPS URL.
- `SUPABASE_SECRET_KEY`: backend-only secret API key, set in Render's encrypted environment editor. Legacy service-role JWT is also supported. Never put this in Vite variables or source control.
- `STORAGE_BACKEND=supabase`, `SUPABASE_BUCKET=receipts`, `COOKIE_SECURE=true`, `SERVE_FRONTEND=true`.
- `FRONTEND_ORIGINS`: optional JSON list of exact HTTPS public origins. With Render's assigned domain, the startup script uses `RENDER_EXTERNAL_URL` automatically. Set explicitly when adding a custom domain.

Startup validates persistent storage, runs Alembic migrations, enables RLS and revokes direct anon/authenticated Data API access on app-owned tables. The app uses its existing Argon2/session/CSRF authentication; Supabase Auth is not used. Only the backend authenticates users and retrieves private receipt objects.

The Docker build context excludes `.env`, user receipts, databases, test fixtures, caches and unrelated workspace files. Local accounts/data are **not** migrated automatically. Production starts empty.

## Verification before calling deployment complete

Run backend tests and frontend build. Confirm Docker cloud build and startup, HTTPS `/api/health`, registration/login/logout, PNG/PDF OCR, confirmation/investigation and report export. Restart the cloud service and verify a test account's receipt and image survive. Check another account cannot retrieve that receipt. Confirm the bucket remains private and app tables have RLS. Test the long-receipt fixtures against the free host's memory budget.

## Free-tier limitations

As checked on 19 October 2026, Render free services sleep after 15 minutes idle; Supabase free projects can pause after a week of inactivity. Free Supabase includes 500 MB database and 1 GB object storage. Keep usage within plan limits; do not upgrade or enable paid compute automatically. Free Render is a demo/hobby target, not an always-on production guarantee. Cold starts and constrained memory may affect large OCR uploads. No paid plan or user-data migration is implied by this setup.

Sources: https://render.com/docs/free and https://supabase.com/pricing.
