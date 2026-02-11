# MOTD Documentation

Complete documentation for the MOTD (Meal of the Day) ordering platform.

---

## 📚 Documentation Index

### Quick Start
- **[CICD_QUICKSTART.md](./CICD_QUICKSTART.md)** - 5-minute CI/CD setup guide
  - Service account creation
  - GitHub connection
  - Trigger configuration

### Deployment & DevOps
- **[DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md)** - Architecture overview and deployment status
  - Live URLs and service endpoints
  - Infrastructure architecture
  - Current deployment state

- **[DEVOPS_GCP_SETUP.md](./DEVOPS_GCP_SETUP.md)** - Complete GCP infrastructure setup
  - Step-by-step runbook
  - Cloud Run, Firebase, Secret Manager
  - Manual deployment procedures

- **[CICD_SETUP.md](./CICD_SETUP.md)** - Detailed CI/CD documentation
  - Service account architecture
  - Build configuration deep-dive
  - Troubleshooting guide
  - Advanced configuration

- **[DOCKER_DEPLOY.md](./DOCKER_DEPLOY.md)** - Docker deployment guide
  - Local Docker setup
  - Container configuration
  - Docker Compose workflows

---

## 🚀 Getting Started

### For Developers
1. Start with the main [README.md](../README.md) for project overview
2. Set up local environment (see README.md)
3. Review [DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md) for architecture

### For DevOps
1. **First time setup**: [DEVOPS_GCP_SETUP.md](./DEVOPS_GCP_SETUP.md)
2. **CI/CD setup**: [CICD_QUICKSTART.md](./CICD_QUICKSTART.md)
3. **Troubleshooting**: [CICD_SETUP.md](./CICD_SETUP.md#troubleshooting)

### For Deployments
- **Automatic**: Push to `main` branch (see [CICD_QUICKSTART.md](./CICD_QUICKSTART.md))
- **Manual**: See deployment scripts in [DEVOPS_GCP_SETUP.md](./DEVOPS_GCP_SETUP.md)

---

## 🌐 Live Environments

| Environment | URL | Status |
|-------------|-----|--------|
| **Production Frontend** | https://emss-487012.web.app | ✅ Live |
| **Production Backend** | https://motd-backend-1008906809776.us-central1.run.app | ✅ Live |
| **Cloud Build** | [Build History](https://console.cloud.google.com/cloud-build/builds?project=emss-487012) | ✅ Active |

---

## 🔧 Common Tasks

### Deploy Backend
```bash
# Automatic (recommended)
git push origin main  # Triggers Cloud Build

# Manual
docker buildx build --platform linux/amd64 -t us-central1-docker.pkg.dev/emss-487012/motd/motd-backend:latest .
docker push us-central1-docker.pkg.dev/emss-487012/motd/motd-backend:latest
gcloud run deploy motd-backend --image=us-central1-docker.pkg.dev/emss-487012/motd/motd-backend:latest --region=us-central1
```

### Deploy Frontend
```bash
# Automatic (recommended)
git push origin main  # Triggers Cloud Build

# Manual
./deploy-frontend.sh
```

### Run Database Migrations
```bash
# Temporarily enable migrations
gcloud run services update motd-backend --region=us-central1 --set-env-vars=RUN_MIGRATIONS=1
sleep 30
gcloud run services update motd-backend --region=us-central1 --set-env-vars=RUN_MIGRATIONS=0
```

### View Logs
```bash
# Backend logs
gcloud run services logs read motd-backend --region=us-central1 --limit=50

# Build logs
gcloud builds list --limit=5
gcloud builds log <BUILD_ID>
```

---

## 📖 Document Purposes

| Document | What's Inside | When to Use |
|----------|---------------|-------------|
| **CICD_QUICKSTART.md** | Fast setup, essential steps only | Setting up CI/CD for the first time |
| **CICD_SETUP.md** | Complete CI/CD reference, troubleshooting | Debugging builds, advanced config |
| **DEPLOYMENT_SUMMARY.md** | Architecture, URLs, current state | Understanding the system, onboarding |
| **DEVOPS_GCP_SETUP.md** | Infrastructure setup, manual procedures | Initial GCP setup, manual deployments |
| **DOCKER_DEPLOY.md** | Docker and local development | Local development, Docker workflows |

---

## 🆘 Need Help?

1. **Build failing?** → [CICD_SETUP.md#troubleshooting](./CICD_SETUP.md#troubleshooting)
2. **Service not responding?** → [DEPLOYMENT_SUMMARY.md#quick-troubleshooting](./DEPLOYMENT_SUMMARY.md#quick-troubleshooting)
3. **First time setup?** → [CICD_QUICKSTART.md](./CICD_QUICKSTART.md)
4. **Understanding architecture?** → [DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md)

---

**Last Updated**: 2026-02-11
