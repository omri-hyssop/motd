# CI/CD Quick Start

**5-minute setup guide** for Cloud Build + GitHub integration.

Full documentation: [CICD_SETUP.md](./CICD_SETUP.md)

---

## Prerequisites ✅

Already configured:
- Cloud Build API enabled
- Build configs created (`cloudbuild-backend.yaml`, `cloudbuild-frontend.yaml`)

**⚠️ IMPORTANT**: You must complete service account setup before creating triggers!

---

## Setup (4 steps)

### 0. Create Cloud Build Service Account (REQUIRED - One Time)

**Create Service Account**:
1. Go to [IAM & Admin → Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts?project=emss-487012)
2. Click **"+ CREATE SERVICE ACCOUNT"**
3. Name: `cloud-build-sa`, Description: `Service account for Cloud Build deployments`
4. Grant roles:
   - Cloud Run Admin
   - Service Account User
   - Firebase Admin
   - Artifact Registry Writer
   - Artifact Registry Reader
   - Logs Writer

**Grant Runtime Access to Secrets**:
1. Go to [Secret Manager](https://console.cloud.google.com/security/secret-manager?project=emss-487012)
2. For EACH secret (`motd-database-url`, `motd-secret-key`, `motd-jwt-secret-key`, `motd-task-trigger-token`):
   - Click secret → **PERMISSIONS** tab → **+ GRANT ACCESS**
   - Principal: `1008906809776-compute@developer.gserviceaccount.com`
   - Role: **Secret Manager Secret Accessor**

**Why?** Cloud Build uses `cloud-build-sa` to deploy, but Cloud Run uses the Compute Engine default SA at runtime to access secrets.

---

### 1. Connect GitHub Repository

```bash
# Open Cloud Build Triggers page
open "https://console.cloud.google.com/cloud-build/triggers?project=emss-487012"
```

- Click **"Connect Repository"**
- Choose **"GitHub (Cloud Build GitHub App)"**
- Authenticate and select your repository
- Click **"Connect"**

### 2. Create Backend Trigger

Click **"Create Trigger"** and configure:

- **Name**: `deploy-backend`
- **Event**: Push to a branch
- **Branch**: `^main$`
- **Build config**: Cloud Build configuration file
- **Location**: `/cloudbuild-backend.yaml`
- **Service account**: `cloud-build-sa@emss-487012.iam.gserviceaccount.com` ⭐
- **Included files** (optional):
  ```
  app/**
  migrations/**
  requirements.txt
  Dockerfile
  cloudbuild-backend.yaml
  ```

Click **"Create"**

### 3. Create Frontend Trigger

Click **"Create Trigger"** and configure:

- **Name**: `deploy-frontend`
- **Event**: Push to a branch
- **Branch**: `^main$`
- **Build config**: Cloud Build configuration file
- **Location**: `/cloudbuild-frontend.yaml`
- **Service account**: `cloud-build-sa@emss-487012.iam.gserviceaccount.com` ⭐
- **Included files** (optional):
  ```
  frontend/**
  firebase.json
  .firebaserc
  cloudbuild-frontend.yaml
  ```

Click **"Create"**

---

## Test It! 🚀

```bash
# Push to GitHub
git add .
git commit -m "Add CI/CD configuration"
git push origin main

# Watch builds
gcloud builds list --project=emss-487012 --limit=5

# Or view in console
open "https://console.cloud.google.com/cloud-build/builds?project=emss-487012"
```

---

## What Happens on Push?

1. **GitHub** receives your push
2. **Cloud Build** automatically starts both pipelines (if files changed)
3. **Backend pipeline** (~3-5 min):
   - Builds Docker image
   - Pushes to Artifact Registry
   - Deploys to Cloud Run
4. **Frontend pipeline** (~2-3 min):
   - Runs `npm install` and `npm run build`
   - Deploys to Firebase Hosting

---

## Verify Deployments

- **Backend**: https://motd-backend-1008906809776.us-central1.run.app
- **Frontend**: https://emss-487012.web.app

---

## Common Commands

```bash
# View recent builds
gcloud builds list --limit=10

# View build logs
gcloud builds log <BUILD_ID>

# Manually trigger backend build
gcloud builds submit --config=cloudbuild-backend.yaml

# Manually trigger frontend build
gcloud builds submit --config=cloudbuild-frontend.yaml

# View Cloud Run revisions
gcloud run revisions list --service=motd-backend --region=us-central1
```

---

## Troubleshooting

**Build not triggering?**
- Check trigger is enabled in Cloud Build console
- Verify branch name matches trigger pattern
- Check included files filter (if set)

**Build failing?**
- View logs in Cloud Build console
- Check service account permissions
- Verify secrets exist in Secret Manager

**Need help?**
- Full docs: [CICD_SETUP.md](./CICD_SETUP.md)
- Build history: `gcloud builds list`
- Cloud Run logs: `gcloud run services logs read motd-backend --region=us-central1`

---

## Next Steps

- [ ] Test a deployment by pushing a small change
- [ ] Set up build notifications
- [ ] Configure staging environment
- [ ] Add automated tests to pipeline
