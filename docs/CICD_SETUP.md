# CI/CD Setup with Cloud Build + GitHub

This document describes the CI/CD pipeline setup for automatic deployments to GCP.

## Overview

- **Source**: GitHub repository
- **CI/CD**: Google Cloud Build
- **Backend**: Automatically builds Docker image, pushes to Artifact Registry, deploys to Cloud Run
- **Frontend**: Automatically builds React app, deploys to Firebase Hosting

---

## ✅ Prerequisites Completed

- [x] Cloud Build API enabled
- [x] Cloud Build service account granted permissions:
  - `roles/run.admin` - Deploy to Cloud Run
  - `roles/iam.serviceAccountUser` - Act as service accounts
  - `roles/firebase.admin` - Deploy to Firebase Hosting
- [x] Build configuration files created:
  - `cloudbuild-backend.yaml` - Backend deployment pipeline
  - `cloudbuild-frontend.yaml` - Frontend deployment pipeline
- [x] `.gcloudignore` created to optimize build performance

---

## Setup Instructions

### Step 0: Create Cloud Build Service Account (REQUIRED)

Cloud Build requires a dedicated service account with proper permissions.

#### Create Service Account

1. **Go to IAM & Admin → Service Accounts**:
   ```
   https://console.cloud.google.com/iam-admin/serviceaccounts?project=emss-487012
   ```

2. **Click "+ CREATE SERVICE ACCOUNT"**

3. **Fill in details**:
   - **Service account name**: `cloud-build-sa`
   - **Service account ID**: `cloud-build-sa`
   - **Description**: `Service account for Cloud Build deployments`

4. **Click "CREATE AND CONTINUE"**

5. **Grant these roles** (click "+ ADD ANOTHER ROLE" for each):
   - ✅ **Cloud Run Admin** (`roles/run.admin`)
   - ✅ **Service Account User** (`roles/iam.serviceAccountUser`)
   - ✅ **Firebase Admin** (`roles/firebase.admin`)
   - ✅ **Artifact Registry Writer** (`roles/artifactregistry.writer`)
   - ✅ **Artifact Registry Reader** (`roles/artifactregistry.reader`)
   - ✅ **Logs Writer** (`roles/logging.logWriter`)

6. **Click "CONTINUE"** then **"DONE"**

#### Grant Cloud Run Runtime Service Account Access to Secrets

**IMPORTANT**: Cloud Run uses a different service account at runtime to access secrets. You must grant the Compute Engine default service account access to Secret Manager.

1. **Go to Secret Manager**:
   ```
   https://console.cloud.google.com/security/secret-manager?project=emss-487012
   ```

2. **For EACH secret**, grant access:
   - Click on: `motd-database-url`
   - Click **"PERMISSIONS"** tab
   - Click **"+ GRANT ACCESS"**
   - **Add principal**: `1008906809776-compute@developer.gserviceaccount.com`
   - **Role**: Secret Manager Secret Accessor
   - Click **"SAVE"**

   Repeat for:
   - `motd-secret-key`
   - `motd-jwt-secret-key`
   - `motd-task-trigger-token`

**Service Account Architecture**:
```
Cloud Build SA (cloud-build-sa)
  ↓ Deploys the service
Cloud Run Service
  ↓ Uses at runtime
Compute Engine Default SA (1008906809776-compute@...)
  ↓ Accesses
Secret Manager Secrets
```

---

### Step 1: Connect GitHub to Cloud Build

1. **Go to Cloud Build Triggers page**:
   ```bash
   open "https://console.cloud.google.com/cloud-build/triggers?project=emss-487012"
   ```
   Or navigate manually: GCP Console → Cloud Build → Triggers

2. **Connect Repository**:
   - Click **"Connect Repository"** or **"Create Trigger"**
   - Select **"GitHub (Cloud Build GitHub App)"**
   - Click **"Authenticate"** and sign in to GitHub
   - Select your GitHub repository
   - Click **"Connect"**

### Step 2: Create Backend Trigger

1. Click **"Create Trigger"**
2. Configure:
   - **Name**: `deploy-backend`
   - **Description**: `Deploy backend to Cloud Run on main branch push`
   - **Event**: Push to a branch
   - **Source**:
     - **Repository**: Your connected repository
     - **Branch**: `^main$` (regex pattern)
   - **Configuration**:
     - **Type**: Cloud Build configuration file (yaml or json)
     - **Location**: `/cloudbuild-backend.yaml`
   - **Service account**: Select `cloud-build-sa@emss-487012.iam.gserviceaccount.com` ⭐
   - **Included files filter (optional)**:
     ```
     app/**
     migrations/**
     requirements.txt
     Dockerfile
     cloudbuild-backend.yaml
     ```
     (This ensures backend only rebuilds when backend files change)

3. Click **"Create"**

### Step 3: Create Frontend Trigger

1. Click **"Create Trigger"**
2. Configure:
   - **Name**: `deploy-frontend`
   - **Description**: `Deploy frontend to Firebase Hosting on main branch push`
   - **Event**: Push to a branch
   - **Source**:
     - **Repository**: Your connected repository
     - **Branch**: `^main$` (regex pattern)
   - **Configuration**:
     - **Type**: Cloud Build configuration file (yaml or json)
     - **Location**: `/cloudbuild-frontend.yaml`
   - **Service account**: Select `cloud-build-sa@emss-487012.iam.gserviceaccount.com` ⭐
   - **Included files filter (optional)**:
     ```
     frontend/**
     firebase.json
     .firebaserc
     cloudbuild-frontend.yaml
     ```
     (This ensures frontend only rebuilds when frontend files change)

3. Click **"Create"**

### Step 4: Test the Pipeline

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add CI/CD pipeline configuration"
   git push origin main
   ```

2. **Monitor builds**:
   - Go to Cloud Build → History
   - Or run: `gcloud builds list --project=emss-487012 --limit=5`
   - Watch the build logs in real-time

3. **Verify deployments**:
   - Backend: https://motd-backend-1008906809776.us-central1.run.app
   - Frontend: https://emss-487012.web.app

---

## Build Configuration Details

### Backend Pipeline (`cloudbuild-backend.yaml`)

**Steps:**
1. **Build**: Creates Docker image with `linux/amd64` platform
2. **Push**: Pushes image to Artifact Registry with commit SHA and `latest` tags
3. **Deploy**: Deploys to Cloud Run with secrets and environment variables

**Duration**: ~3-5 minutes

**Triggers on changes to**:
- `app/` directory
- `migrations/` directory
- `requirements.txt`
- `Dockerfile`
- `cloudbuild-backend.yaml`

### Frontend Pipeline (`cloudbuild-frontend.yaml`)

**Steps:**
1. **Install**: Runs `npm install` in frontend directory
2. **Build**: Builds production bundle with Vite
3. **Deploy**: Deploys to Firebase Hosting

**Duration**: ~2-3 minutes

**Triggers on changes to**:
- `frontend/` directory
- `firebase.json`
- `.firebaserc`
- `cloudbuild-frontend.yaml`

---

## Database Migrations

### Automatic Migrations (Use with Caution)

By default, migrations are **disabled** (`RUN_MIGRATIONS=0`).

To enable automatic migrations on deploy, uncomment the migration steps in `cloudbuild-backend.yaml`:

```yaml
# Optional: Run migrations (only enable when needed)
- name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
  entrypoint: gcloud
  args:
    - 'run'
    - 'services'
    - 'update'
    - 'motd-backend'
    - '--region=us-central1'
    - '--set-env-vars=RUN_MIGRATIONS=1'
  id: 'enable-migrations'
  waitFor: ['deploy-cloud-run']

# ... wait and disable steps
```

**⚠️ Warning**: Auto-migrations can be risky. For production, consider:
- Running migrations manually via Cloud Run job
- Using separate staging environment
- Testing migrations before production deploy

### Manual Migrations

To run migrations manually:

```bash
# Temporarily enable migrations
gcloud run services update motd-backend \
  --region=us-central1 \
  --set-env-vars=RUN_MIGRATIONS=1 \
  --project=emss-487012

# Wait 30 seconds for service to restart and run migrations
sleep 30

# Disable migrations
gcloud run services update motd-backend \
  --region=us-central1 \
  --set-env-vars=RUN_MIGRATIONS=0 \
  --project=emss-487012
```

---

## Advanced Configuration

### Environment Variables

To add/update environment variables:

**Backend** (in `cloudbuild-backend.yaml`):
```yaml
- '--set-env-vars=RUN_MIGRATIONS=0,NEW_VAR=value'
```

**Frontend** (in `cloudbuild-frontend.yaml`):
```yaml
env:
  - 'VITE_API_BASE_URL=https://motd-backend-1008906809776.us-central1.run.app/api'
  - 'VITE_NEW_VAR=value'
```

### Secrets

Backend secrets are managed via Secret Manager. To add a new secret:

```bash
# Create secret
echo -n "secret-value" | gcloud secrets create secret-name \
  --data-file=- \
  --project=emss-487012

# Grant access to Cloud Build service account
gcloud secrets add-iam-policy-binding secret-name \
  --member="serviceAccount:1008906809776@cloudbuild.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=emss-487012

# Update cloudbuild-backend.yaml
# Add to --set-secrets: SECRET_NAME=secret-name:latest
```

### Build Timeout

Default timeout is 20 minutes (backend) and 10 minutes (frontend). To adjust:

```yaml
timeout: '1200s'  # 20 minutes
```

### Machine Type

Default is `E2_HIGHCPU_8` for faster builds. To adjust:

```yaml
options:
  machineType: 'E2_HIGHCPU_8'  # or E2_HIGHCPU_4, N1_HIGHCPU_8, etc.
```

---

## Troubleshooting

### Build Fails: Permission Denied

**Issue**: Cloud Build can't access secrets or deploy to Cloud Run

**Solution**: Verify service account permissions:
```bash
gcloud projects get-iam-policy emss-487012 \
  --flatten="bindings[].members" \
  --filter="bindings.members:*cloudbuild.gserviceaccount.com"
```

Should show:
- `roles/run.admin`
- `roles/iam.serviceAccountUser`
- `roles/firebase.admin`

### Backend Deploy Fails: Permission Denied on Secrets

**Issue**: Build succeeds but deploy fails with:
```
ERROR: Permission denied on secret: projects/.../secrets/motd-database-url/versions/latest
for Revision service account 1008906809776-compute@developer.gserviceaccount.com
```

**Root Cause**: Cloud Run runtime service account (Compute Engine default) doesn't have access to secrets.

**Solution**: Grant Secret Manager access to the runtime service account:

**Via Console**:
1. Go to [Secret Manager](https://console.cloud.google.com/security/secret-manager?project=emss-487012)
2. For each secret (`motd-database-url`, `motd-secret-key`, `motd-jwt-secret-key`, `motd-task-trigger-token`):
   - Click secret → **PERMISSIONS** → **+ GRANT ACCESS**
   - Principal: `1008906809776-compute@developer.gserviceaccount.com`
   - Role: **Secret Manager Secret Accessor**

**Via CLI**:
```bash
for SECRET in motd-database-url motd-secret-key motd-jwt-secret-key motd-task-trigger-token; do
  gcloud secrets add-iam-policy-binding $SECRET \
    --member="serviceAccount:1008906809776-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --project=emss-487012
done
```

**Remember**: Two service accounts are involved:
- **Cloud Build SA** (`cloud-build-sa`) - Deploys the service
- **Compute Engine Default SA** (`1008906809776-compute@...`) - Runs the service and accesses secrets

### Artifact Registry Permission Denied

**Issue**: Build fails with:
```
denied: Permission 'artifactregistry.repositories.uploadArtifacts' denied
```

**Solution**: Grant Artifact Registry Writer role to Cloud Build service account:
1. Go to [IAM & Admin](https://console.cloud.google.com/iam-admin/iam?project=emss-487012)
2. Find `cloud-build-sa@emss-487012.iam.gserviceaccount.com`
3. Edit and add role: **Artifact Registry Writer**

### Frontend Build Fails: Firebase Deploy Error

**Issue**: Firebase deploy fails with authentication error

**Solution**: Cloud Build service account needs `roles/firebase.admin`:
```bash
gcloud projects add-iam-policy-binding emss-487012 \
  --member="serviceAccount:1008906809776@cloudbuild.gserviceaccount.com" \
  --role="roles/firebase.admin"
```

### Build Takes Too Long

**Issue**: Build timeout or slow builds

**Solutions**:
1. Check `.gcloudignore` is properly excluding unnecessary files
2. Increase machine type in cloudbuild.yaml
3. Use Docker layer caching (add `--cache-from` flag)
4. For frontend: Consider caching node_modules

### Backend Deploy Succeeds but App Crashes

**Issue**: Container starts but app fails

**Debug**:
1. Check Cloud Run logs:
   ```bash
   gcloud run services logs read motd-backend \
     --region=us-central1 \
     --limit=50
   ```

2. Verify secrets are accessible:
   ```bash
   gcloud run services describe motd-backend \
     --region=us-central1 \
     --format="value(spec.template.spec.containers[0].env)"
   ```

3. Check database connectivity from Cloud Run

---

## Manual Build Trigger

To manually trigger a build without pushing to GitHub:

```bash
# Backend
gcloud builds submit \
  --config=cloudbuild-backend.yaml \
  --project=emss-487012

# Frontend
gcloud builds submit \
  --config=cloudbuild-frontend.yaml \
  --project=emss-487012
```

---

## Cost Optimization

### Free Tier (as of 2026)
- **Cloud Build**: 120 build-minutes/day free
- **Artifact Registry**: 0.5 GB storage free
- **Cloud Run**: 2 million requests/month free
- **Firebase Hosting**: 10 GB storage + 360 MB/day transfer free

### Tips to Reduce Costs
1. Use file filters on triggers to avoid unnecessary builds
2. Use appropriate machine types (E2_HIGHCPU_4 vs E2_HIGHCPU_8)
3. Clean up old images in Artifact Registry
4. Monitor build frequency and duration

---

## Next Steps

- [ ] Set up staging environment with separate triggers
- [ ] Add automated testing to CI pipeline
- [ ] Set up build notifications (Slack, email, etc.)
- [ ] Implement blue-green deployments
- [ ] Add performance monitoring

---

## Resources

- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Cloud Run Continuous Deployment](https://cloud.google.com/run/docs/continuous-deployment)
- [Firebase Hosting with Cloud Build](https://firebase.google.com/docs/hosting/cloud-build-integration)
