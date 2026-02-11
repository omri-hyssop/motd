# GCP DevOps Setup (Cloud Run + Supabase)

Goal:
- Backend: Cloud Run (container)
- Frontend: Static hosting (Firebase Hosting recommended for SPA) **or** Cloud Storage + HTTPS LB/CDN
- DB: Supabase Postgres (set `DATABASE_URL`)
- Cron/scheduled tasks: Cloud Scheduler → backend task trigger endpoint

This file is a **bit-for-bit runbook**. You run the commands; we’ll adjust as needed.

---

## Current status (as of 2026-02-10)

✅ Completed:
- GCP project: `emss-487012`
- Region: `us-central1`
- Enabled APIs: Cloud Run, Artifact Registry, Cloud Build, Secret Manager, Cloud Scheduler, Firebase Hosting
- Artifact Registry repo created: `motd` (Docker)
- Secrets created in Secret Manager:
  - `motd-database-url` (placeholder first, later updated to Supabase `DATABASE_URL`)
  - `motd-secret-key`
  - `motd-jwt-secret-key`
  - `motd-task-trigger-token`
- Backend image built/pushed as `linux/amd64` (Apple Silicon fix via `docker buildx`)
- Backend deployed to Cloud Run service `motd-backend` (kept **private**, org policy blocks `allUsers`):
  - Service URL: `https://motd-backend-1008906809776.us-central1.run.app`
- One-off DB migrations executed by temporarily setting `RUN_MIGRATIONS=1`, then reverting to `RUN_MIGRATIONS=0`
- Cloud Scheduler set up to call the backend task trigger endpoint using OIDC + `X-Task-Token` (no public invoker needed)
- **Frontend deployed to Firebase Hosting** (solution to GCS public access restriction):
  - Hosting URL: `https://emss-487012.web.app`
  - Firebase bypasses the org policy restrictions that blocked GCS public access
  - Frontend successfully connects to Cloud Run backend
- **CI/CD pipeline configured with Cloud Build + GitHub**:
  - Cloud Build service account granted necessary permissions (run.admin, iam.serviceAccountUser, firebase.admin)
  - Backend pipeline: `cloudbuild-backend.yaml` (build → push → deploy to Cloud Run)
  - Frontend pipeline: `cloudbuild-frontend.yaml` (build → deploy to Firebase Hosting)
  - Ready to connect GitHub repository and create triggers (see `CICD_SETUP.md`)

✅ Resolved:
- ~~Public frontend hosting via GCS blocked by org policy~~ → **Solved with Firebase Hosting**
  - Firebase Hosting doesn't suffer from the same `allUsers` org policy restrictions
  - Previous attempts with GCS + Load Balancer failed due to org restrictions on public bucket access
  - Firebase Hosting is the recommended approach for this org's security policies

📝 Notes on org restrictions:
- This GCP org/project blocks public access patterns (`allUsers`) for:
  - Cloud Run public invoker bindings
  - GCS bucket public access (`allUsers:objectViewer`)
- Firebase Hosting successfully bypasses these restrictions
- If future services need public access, coordinate with GCP org admin or use Firebase-managed services

---

## 0) Decide values (copy/paste)

Pick these once:
```bash
export PROJECT_ID="emss-487012"
export REGION="us-central1"
export AR_REPO="motd"
export SERVICE_BACKEND="motd-backend"
```

Optional (recommended):
```bash
export SERVICE_FRONTEND="motd-frontend"
```

Set your gcloud project:
```bash
gcloud config set project "$PROJECT_ID"
```

Confirm:
```bash
gcloud config list --format='text(core.project,core.account)'
```

---

## 1) Authenticate (when needed)

Interactive login:
```bash
gcloud auth login
```

Application Default Credentials (often needed by local tools):
```bash
gcloud auth application-default login
```

If you ever see “no active account selected”:
```bash
gcloud auth list
gcloud config set account "you@example.com"
```

---

## 2) Enable required APIs (one-time per project)

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  cloudscheduler.googleapis.com
```

---

## 3) Create Artifact Registry repo (one-time)

Create the repo:
```bash
gcloud artifacts repositories create "$AR_REPO" \
  --repository-format=docker \
  --location="$REGION"
```

Configure Docker auth:
```bash
gcloud auth configure-docker "$REGION-docker.pkg.dev"
```

---

## 4) Create secrets (placeholder first)

We’ll store secrets in Secret Manager and bind them to Cloud Run.

### 4.1 DATABASE_URL (placeholder)

Create placeholder now (replace later after you create Supabase):
```bash
printf '%s' "postgresql://USER:PASSWORD@HOST:5432/DBNAME" | \
  gcloud secrets create motd-database-url --data-file=-
```

Later, update it with the real Supabase URL:
```bash
printf '%s' "postgresql://REAL..." | \
  gcloud secrets versions add motd-database-url --data-file=-
```

### 4.2 Flask/JWT secrets

Generate strong randoms (macOS/Linux):
```bash
python3 - <<'PY'
import secrets
print("SECRET_KEY=" + secrets.token_urlsafe(48))
print("JWT_SECRET_KEY=" + secrets.token_urlsafe(48))
print("TASK_TRIGGER_TOKEN=" + secrets.token_urlsafe(48))
PY
```

Create secrets (paste values in place of `...`):
```bash
printf '%s' "..." | gcloud secrets create motd-secret-key --data-file=-
printf '%s' "..." | gcloud secrets create motd-jwt-secret-key --data-file=-
printf '%s' "..." | gcloud secrets create motd-task-trigger-token --data-file=-
```

---

## 5) Build + push backend image

From repo root:
```bash
export IMAGE_BACKEND="$REGION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/backend:$(git rev-parse --short HEAD)"
docker buildx create --use --name motd-builder 2>/dev/null || docker buildx use motd-builder
docker buildx build --platform linux/amd64 -t "$IMAGE_BACKEND" --push .
```

---

## 6) Deploy backend to Cloud Run

Notes:
- Backend is already set up to listen on `$PORT` (Cloud Run requirement).
- If your org blocks public access, do **not** grant `allUsers` invoker. Keep the service private and use identity tokens/OIDC.
- Best practice on Cloud Run: keep `SCHEDULER_ENABLED=false` and use Cloud Scheduler instead.
- We start with `RUN_MIGRATIONS=0` to avoid “every instance runs migrations” surprises.

Deploy:
```bash
gcloud run deploy "$SERVICE_BACKEND" \
  --region="$REGION" \
  --image="$IMAGE_BACKEND" \
  --allow-unauthenticated \
  --set-env-vars="FLASK_ENV=production,SCHEDULER_ENABLED=false,RUN_MIGRATIONS=0,WAIT_FOR_DB=1,LOG_LEVEL=INFO,LOG_FILE=/tmp/app.log" \
  --set-secrets="DATABASE_URL=motd-database-url:latest,SECRET_KEY=motd-secret-key:latest,JWT_SECRET_KEY=motd-jwt-secret-key:latest,TASK_TRIGGER_TOKEN=motd-task-trigger-token:latest"
```

Get the URL:
```bash
export BACKEND_URL="$(gcloud run services describe "$SERVICE_BACKEND" --region "$REGION" --format='value(status.url)')"
echo "$BACKEND_URL"
```

Health check:
```bash
curl -sf -H "Authorization: Bearer $(gcloud auth print-identity-token)" "$BACKEND_URL/api/health"
```

---

## 7) CORS + FRONTEND_URL (set once you have a frontend URL)

The backend must allow your browser frontend to call it. Once you know the frontend origin, set:
- `FRONTEND_URL` (one URL)
- `CORS_ORIGINS` (comma-separated list of allowed origins)

Example (replace with your real frontend URL):
```bash
gcloud run services update "$SERVICE_BACKEND" \
  --region="$REGION" \
  --set-env-vars="FRONTEND_URL=https://YOUR_FRONTEND_URL,CORS_ORIGINS=https://YOUR_FRONTEND_URL"
```

---

## 8) Scheduled jobs (Cloud Scheduler → /api/tasks/run)

The backend exposes `POST /api/tasks/run` and requires header `X-Task-Token`.

Fetch the token (from Secret Manager) into a shell var:
```bash
export TASK_TOKEN="$(gcloud secrets versions access latest --secret=motd-task-trigger-token)"
```

If your Cloud Run service is private, configure Scheduler to use OIDC:
```bash
export SCHEDULER_SA="motd-scheduler"
export SCHEDULER_SA_EMAIL="${SCHEDULER_SA}@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud iam service-accounts create "$SCHEDULER_SA" --display-name="MOTD Cloud Scheduler invoker"
gcloud run services add-iam-policy-binding "$SERVICE_BACKEND" \
  --region "$REGION" \
  --member="serviceAccount:${SCHEDULER_SA_EMAIL}" \
  --role="roles/run.invoker"
```

Create a daily reminders job (edit schedule/timezone later):
```bash
gcloud scheduler jobs create http motd-daily-reminders \
  --location "$REGION" \
  --schedule "0 10 * * *" \
  --uri "$BACKEND_URL/api/tasks/run" \
  --http-method POST \
  --oidc-service-account-email "$SCHEDULER_SA_EMAIL" \
  --oidc-token-audience "$BACKEND_URL" \
  --headers "Content-Type=application/json,X-Task-Token=$TASK_TOKEN" \
  --message-body '{"task":"daily_reminders"}'
```

Create restaurant summaries (example: 11:00):
```bash
gcloud scheduler jobs create http motd-restaurant-summaries \
  --location "$REGION" \
  --schedule "0 11 * * *" \
  --uri "$BACKEND_URL/api/tasks/run" \
  --http-method POST \
  --oidc-service-account-email "$SCHEDULER_SA_EMAIL" \
  --oidc-token-audience "$BACKEND_URL" \
  --headers "Content-Type=application/json,X-Task-Token=$TASK_TOKEN" \
  --message-body '{"task":"restaurant_summaries"}'
```

Create nightly cleanup (00:00):
```bash
gcloud scheduler jobs create http motd-cleanup-sessions \
  --location "$REGION" \
  --schedule "0 0 * * *" \
  --uri "$BACKEND_URL/api/tasks/run" \
  --http-method POST \
  --oidc-service-account-email "$SCHEDULER_SA_EMAIL" \
  --oidc-token-audience "$BACKEND_URL" \
  --headers "Content-Type=application/json,X-Task-Token=$TASK_TOKEN" \
  --message-body '{"task":"cleanup_old_sessions"}'
```

---

## 9) Supabase (when ready)

In Supabase:
- Create project
- Get Postgres connection string (use the “Connection string” / “URI”)

Then update `motd-database-url` (see step 4.1) and redeploy backend (or just restart):
```bash
gcloud run services update "$SERVICE_BACKEND" --region="$REGION"
```

---

## 10) Migrations (after DB is real)

Simplest approach:
- Temporarily set `RUN_MIGRATIONS=1`, deploy once, then set it back to `0`.

```bash
gcloud run services update "$SERVICE_BACKEND" \
  --region="$REGION" \
  --set-env-vars="RUN_MIGRATIONS=1"
```

Wait for a deployment, then:
```bash
gcloud run services update "$SERVICE_BACKEND" \
  --region="$REGION" \
  --set-env-vars="RUN_MIGRATIONS=0"
```

---

## 10.5) Create the first admin user (production)

Preferred method: run a **Cloud Run Job** using the same image/secrets as the backend, so it runs “inside GCP” (no laptop DNS/VPN issues).

### Option A (recommended): Cloud Run Job (runs in GCP)

Get the image Cloud Run is currently using:
```bash
export PROJECT_ID="emss-487012"
export REGION="us-central1"
export SERVICE_BACKEND="motd-backend"

export IMAGE_BACKEND="$(gcloud run services describe "$SERVICE_BACKEND" --project "$PROJECT_ID" --region "$REGION" --format='value(spec.template.spec.containers[0].image)')"
echo "$IMAGE_BACKEND"
```

Create a one-off job (you can delete it afterwards):
```bash
export JOB_NAME="motd-create-admin"

gcloud run jobs create "$JOB_NAME" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --image "$IMAGE_BACKEND" \
  --set-env-vars "FLASK_ENV=production" \
  --set-secrets "DATABASE_URL=motd-database-url:latest,SECRET_KEY=motd-secret-key:latest,JWT_SECRET_KEY=motd-jwt-secret-key:latest" \
  --command "python3" \
  --args "manage.py,create-admin"
```

Execute it by supplying admin details as env vars (recommended to avoid typing secrets in shell history, you can paste interactively in your terminal):
```bash
gcloud run jobs execute "$JOB_NAME" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --update-env-vars "ADMIN_EMAIL=you@example.com,ADMIN_PASSWORD=ChangeMe123!,ADMIN_FIRST_NAME=Admin,ADMIN_LAST_NAME=User" \
  --wait
```

Tip: if you don’t want the password in shell history, set it in your environment first and reference it:
```bash
export ADMIN_PASSWORD='ChangeMe123!'
gcloud run jobs execute "$JOB_NAME" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --update-env-vars "ADMIN_EMAIL=you@example.com,ADMIN_PASSWORD=$ADMIN_PASSWORD,ADMIN_FIRST_NAME=Admin,ADMIN_LAST_NAME=User" \
  --wait
```

Important:
- Cloud Run Jobs are non-interactive. If you forget one of `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_FIRST_NAME`, `ADMIN_LAST_NAME`, the job will fail.

View logs (if needed):
```bash
gcloud run jobs executions list --project "$PROJECT_ID" --region "$REGION" --job "$JOB_NAME" --limit 5
gcloud run jobs executions logs read --project "$PROJECT_ID" --region "$REGION" --job "$JOB_NAME" --limit 200
```

Delete the job once you’re done:
```bash
gcloud run jobs delete "$JOB_NAME" --project "$PROJECT_ID" --region "$REGION" --quiet
```

### Option B: Run locally against production DB (requires laptop network/DNS access to Supabase)

From repo root (uses `manage.py create-admin`, password input is hidden):
```bash
FLASK_ENV=production \
DATABASE_URL="$(gcloud secrets versions access latest --secret=motd-database-url --project emss-487012)" \
SECRET_KEY="$(gcloud secrets versions access latest --secret=motd-secret-key --project emss-487012)" \
JWT_SECRET_KEY="$(gcloud secrets versions access latest --secret=motd-jwt-secret-key --project emss-487012)" \
python3 manage.py create-admin
```

Notes:
- This creates a user row with `role=admin` in the production database.
- If the email already exists, the command prints an error and exits.

---

## 11) Frontend hosting with Firebase Hosting ✅

Firebase Hosting successfully deployed! Here's the complete setup:

### Initial Setup (one-time):
```bash
# 1. Enable Firebase APIs
gcloud services enable firebase.googleapis.com firebasehosting.googleapis.com --project=emss-487012

# 2. Add Firebase to the GCP project via Firebase Console
# Visit: https://console.firebase.google.com/
# Click "Add project" → Select "emss-487012" → Follow prompts

# 3. Create Firebase configuration files (already done):
# - firebase.json (points to frontend/dist)
# - .firebaserc (sets default project to emss-487012)
```

### Deploy Frontend:
```bash
# Build with production backend URL
cd frontend
VITE_API_BASE_URL=https://motd-backend-1008906809776.us-central1.run.app/api npm run build

# Or for convenience, use the .env.production file:
npm run build  # Vite automatically uses .env.production in production mode

# Deploy to Firebase Hosting
cd ..
firebase deploy --only hosting
```

### Result:
- **Hosting URL**: https://emss-487012.web.app
- **Auto SSL**: Provided by Firebase
- **SPA routing**: Configured with rewrites to /index.html
- **CDN**: Global edge caching included
- **No org policy issues**: Firebase bypasses the `allUsers` restrictions that blocked GCS

### Alternative Options (not used):

#### Option B: Cloud Run (frontend container)
Deploy `frontend/` as a second Cloud Run service. Works well, but costs more than static hosting.

#### Option C: Cloud Storage + HTTPS load balancer/CDN
Cheapest at scale, but more setup. Blocked by org policy restrictions on public bucket access.

---

## Appendix: What we tried (frontend on GCS + external HTTP LB)

Goal: Serve the `frontend/dist` static build from a private bucket via load balancer/CDN.

Resources created (names used during setup):
- Backend bucket: `motd-frontend-bucket` → `motd-frontend-emss-487012-1770737723` (CDN enabled)
- URL map: `motd-url-map`
- Target HTTP proxy: `motd-http-proxy`
- Forwarding rule: `motd-http-forwarding-rule` (port 80)
- External IP: `34.128.158.24`

Observed behavior:
- `curl -I http://34.128.158.24/` returns `403 AccessDenied` from Cloud Storage.

Bucket IAM at time of failure:
- Only `1008906809776-compute@developer.gserviceaccount.com` had `roles/storage.objectViewer`.

Notes:
- The standard “make it public” approach (`gsutil iam ch allUsers:objectViewer ...`) is blocked by org policy.
- We attempted to grant a Google-managed LB service account access; one suggested principal did not exist (`service-<PROJECT_NUMBER>@gcp-sa-loadbalancer.iam.gserviceaccount.com`), and subsequent attempts still resulted in 403.

Next decision point:
- **Public app**: requires org admin to permit public access (Cloud Run `allUsers` and/or bucket/LB access pattern).
- **Private app**: deploy the frontend as a private Cloud Run service and put both services behind HTTPS LB + IAP.
