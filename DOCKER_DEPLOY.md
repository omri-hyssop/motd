# Docker Deployment (Local + GCP)

This repo is set up to run **backend** (Flask) and **frontend** (React/Vite) in Docker.

## Local Docker (docker compose)

Run:

```bash
docker compose up -d --build
```

Services:
- Frontend: `http://localhost:8080`
- Backend: `http://localhost:5001`
- DB (Postgres): `localhost:5432` (dev only)

Smoke checks:
```bash
curl -sf http://localhost:5001/api/health
curl -I http://localhost:8080
```

Stop:
```bash
docker compose down -v
```

## GCP (recommended): Cloud Run backend + static frontend

This path prioritizes **low ops** and **cost**:
- Backend runs on **Cloud Run** (pay-per-use).
- Frontend ships as static files to **Cloud Storage** (optionally behind Cloud CDN).
- Database can be **Supabase Postgres** (cheapest/easiest) or **Cloud SQL for Postgres** (all-in-GCP).

### 0) Prereqs

You need:
- `gcloud` installed
- A GCP project + billing enabled
- You authenticated locally: `gcloud auth login`

Pick variables:
```bash
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"
export SERVICE_BACKEND="motd-backend"
export AR_REPO="motd"
```

Set project + enable APIs:
```bash
gcloud config set project "$PROJECT_ID"
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com cloudscheduler.googleapis.com
```

Create an Artifact Registry repo (one-time):
```bash
gcloud artifacts repositories create "$AR_REPO" --repository-format=docker --location="$REGION"
gcloud auth configure-docker "$REGION-docker.pkg.dev"
```

### 1) Backend (Flask) on Cloud Run

Build + push the backend image:
```bash
export IMAGE_BACKEND="$REGION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/backend:$(git rev-parse --short HEAD)"
docker buildx create --use --name motd-builder 2>/dev/null || docker buildx use motd-builder
docker buildx build --platform linux/amd64 -t "$IMAGE_BACKEND" --push .
```

Create secrets (recommended for production):
```bash
printf '%s' "postgresql://..." | gcloud secrets create motd-database-url --data-file=-
printf '%s' "change-me" | gcloud secrets create motd-secret-key --data-file=-
printf '%s' "change-me" | gcloud secrets create motd-jwt-secret-key --data-file=-
printf '%s' "change-me" | gcloud secrets create motd-task-trigger-token --data-file=-
```

Deploy:
```bash
gcloud run deploy "$SERVICE_BACKEND" \
  --region="$REGION" \
  --image="$IMAGE_BACKEND" \
  --allow-unauthenticated \
  --set-env-vars="FLASK_ENV=production,SCHEDULER_ENABLED=false,RUN_MIGRATIONS=0,WAIT_FOR_DB=1,LOG_LEVEL=INFO,LOG_FILE=/tmp/app.log" \
  --set-secrets="DATABASE_URL=motd-database-url:latest,SECRET_KEY=motd-secret-key:latest,JWT_SECRET_KEY=motd-jwt-secret-key:latest,TASK_TRIGGER_TOKEN=motd-task-trigger-token:latest"
```
If your org blocks public access, keep the service private (do not grant `allUsers` invoker) and use identity tokens/OIDC for access.

**Required env vars (minimum)**
- `DATABASE_URL` (Supabase or Cloud SQL)
- `SECRET_KEY`
- `JWT_SECRET_KEY`

**Recommended env vars**
- `FRONTEND_URL` = your frontend URL (Cloud Storage / CDN domain)
- `CORS_ORIGINS` = comma-separated allowed origins, include your frontend URL
- `RUN_MIGRATIONS` = `0` (recommended; run migrations explicitly)
- `SCHEDULER_ENABLED` = `false` (Cloud Run-friendly; use Cloud Scheduler instead)
- `TASK_TRIGGER_TOKEN` = shared secret for `/api/tasks/run` (header `X-Task-Token`)

**Optional (integrations)**
- WhatsApp: `WHATSAPP_API_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_BUSINESS_ACCOUNT_ID`, `WHATSAPP_API_VERSION`, `WHATSAPP_API_URL`
- SendGrid: `SENDGRID_API_KEY`, `FROM_EMAIL`, `FROM_NAME`

**Health endpoint**
- Backend exposes `GET /api/health`

#### Running migrations (recommended: one-off)

The backend image can run migrations via `flask db upgrade`.

Option A (simple): temporarily set `RUN_MIGRATIONS=1`, deploy once, then set it back to `0`.

Option B (cleaner): create a Cloud Run Job that runs `flask db upgrade` against the same image and secrets.

### 2) Frontend (static) on Cloud Storage

Build locally:
```bash
cd frontend
npm ci
VITE_API_BASE_URL="https://$(gcloud run services describe "$SERVICE_BACKEND" --region "$REGION" --format='value(status.url)')/api" npm run build
cd ..
```

Create a bucket and upload:
```bash
export BUCKET="motd-frontend-$PROJECT_ID"
gsutil mb -l "$REGION" "gs://$BUCKET"
gsutil -m rsync -r frontend/dist "gs://$BUCKET"
```

Serve it:
- Easiest: use **Firebase Hosting** (recommended for SPA routing), or
- Cloud Storage website + HTTPS via a Load Balancer / Cloud CDN (more setup).

If you prefer “containers only”, you can deploy the `frontend/` image to Cloud Run as a separate service.

### 3) Scheduled tasks on GCP (Cloud Scheduler)

Cloud Run web instances should keep `SCHEDULER_ENABLED=false`.

Instead, create Cloud Scheduler HTTP jobs that call:
- `POST https://<backend>/api/tasks/run` with JSON `{"task":"daily_reminders"}`
- `POST https://<backend>/api/tasks/run` with JSON `{"task":"restaurant_summaries"}`
- `POST https://<backend>/api/tasks/run` with JSON `{"task":"cleanup_old_sessions"}`

Include header:
- `X-Task-Token: <TASK_TRIGGER_TOKEN>`

Example (daily at 10:00):
```bash
export BACKEND_URL="$(gcloud run services describe "$SERVICE_BACKEND" --region "$REGION" --format='value(status.url)')"
gcloud scheduler jobs create http motd-daily-reminders \
  --location "$REGION" \
  --schedule "0 10 * * *" \
  --uri "$BACKEND_URL/api/tasks/run" \
  --http-method POST \
  --oidc-service-account-email "motd-scheduler@${PROJECT_ID}.iam.gserviceaccount.com" \
  --oidc-token-audience "$BACKEND_URL" \
  --headers "Content-Type=application/json,X-Task-Token=$(gcloud secrets versions access latest --secret=motd-task-trigger-token)" \
  --message-body '{"task":"daily_reminders"}'
```

### Database options (pricing-friendly)

Option A (cheapest/easiest): keep using **Supabase Postgres** and set `DATABASE_URL` accordingly.

Option B (all-in-GCP): **Cloud SQL for Postgres**.
- Create an instance + database + user.
- Configure Cloud Run to connect to Cloud SQL and use a socket-based URL, e.g.:
  `postgresql://USER:PASSWORD@/DBNAME?host=/cloudsql/INSTANCE_CONNECTION_NAME`

## Notes / Gotchas

- The backend image uses `python:3.12-slim` because `psycopg2-binary==2.9.9` doesn’t build cleanly on Python 3.13 in this environment.
- Cloud Run filesystem is **ephemeral**. If you need persistent uploads, store them in **GCS**.
- For production, set strong secrets and restrict `CORS_ORIGINS` to just your frontend domain.
