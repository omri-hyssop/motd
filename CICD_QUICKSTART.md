# CI/CD Quick Start

**5-minute setup guide** for Cloud Build + GitHub integration.

Full documentation: [CICD_SETUP.md](./CICD_SETUP.md)

---

## Prerequisites ✅

Already configured:
- Cloud Build API enabled
- Service account permissions granted
- Build configs created (`cloudbuild-backend.yaml`, `cloudbuild-frontend.yaml`)

---

## Setup (3 steps)

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
