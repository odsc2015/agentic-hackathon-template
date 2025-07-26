#!/bin/bash
set -e
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
BACKEND_SERVICE="life-witness-agent-backend"
FRONTEND_SERVICE="life-witness-agent-frontend"
echo "Building backend Docker image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$BACKEND_SERVICE ./backend
echo "Building frontend Docker image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$FRONTEND_SERVICE ./frontend
echo "Deploying backend to Cloud Run..."
gcloud run deploy $BACKEND_SERVICE \
  --image gcr.io/$PROJECT_ID/$BACKEND_SERVICE \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated
  
echo "Deploying frontend to Cloud Run..."
gcloud run deploy $FRONTEND_SERVICE \
  --image gcr.io/$PROJECT_ID/$FRONTEND_SERVICE \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi
echo "Deployment complete!"
