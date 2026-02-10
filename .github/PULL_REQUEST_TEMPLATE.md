# Pull Request

## Description
<!-- Describe your changes in detail -->

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Changes Made
<!-- List the main changes -->
-
-
-

## Testing
- [ ] Backend tests pass (`pytest`)
- [ ] Frontend builds successfully (`npm run build`)
- [ ] Tested locally
- [ ] Verified deployment in staging/dev

## Database Changes
- [ ] No database changes
- [ ] Migrations included
- [ ] Migrations tested

## Deployment Notes
<!-- Any special deployment steps or considerations -->

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] New and existing tests pass locally

## Screenshots (if applicable)
<!-- Add screenshots for UI changes -->

---

**Note**: When this PR is merged to `main`, Cloud Build will automatically:
- Build and deploy backend to Cloud Run (if backend files changed)
- Build and deploy frontend to Firebase Hosting (if frontend files changed)

Monitor the deployment: https://console.cloud.google.com/cloud-build/builds?project=emss-487012
