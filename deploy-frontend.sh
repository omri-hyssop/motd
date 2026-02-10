#!/bin/bash
set -e

echo "🔨 Building frontend with production backend URL..."
cd frontend
npm run build

echo "🚀 Deploying to Firebase Hosting..."
cd ..
firebase deploy --only hosting

echo "✅ Deployment complete!"
echo "🌐 Visit: https://emss-487012.web.app"
