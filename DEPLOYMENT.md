# Deployment Guide: agents-assemble
`Tharak Vangalapat`

This guide describes how to build, deploy, and access both backend (FastAPI) and frontend (Next.js/React) services for the agents-assemble project on Google Cloud Run using Docker.

---

## Prerequisites
- Google Cloud account and project
- `gcloud` CLI installed and authenticated
- Docker installed
- Node.js and Python installed locally for development
- Required files: `Dockerfile`, `requirements.txt` (backend), `package.json` (frontend), `.env.local` (frontend)

---

## 1. Build and Deploy Backend (FastAPI)

### a. Ensure dependencies
Your `backend/requirements.txt` should include:
```
fastapi
pydantic
uvicorn[standard]
```

### b. Build Docker image locally (optional)
```sh
cd agents-assemble/backend
docker build -t life-witness-agent-backend .
```

### c. Deploy to Google Cloud Run
From the project root, run:
```sh
gcloud builds submit --tag gcr.io/$PROJECT_ID/life-witness-agent-backend ./backend

gcloud run deploy life-witness-agent-backend \
  --image gcr.io/$PROJECT_ID/life-witness-agent-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 2. Build and Deploy Frontend (Next.js/React)

### a. Ensure `.env.local` is present in `frontend/` and not excluded by `.dockerignore`.

### b. Build Docker image locally (optional)
```sh
cd agents-assemble/frontend
docker build -t life-witness-agent-frontend .
```

### c. Deploy to Google Cloud Run
From the project root, run:
```sh
gcloud builds submit --tag gcr.io/$PROJECT_ID/life-witness-agent-frontend ./frontend

gcloud run deploy life-witness-agent-frontend \
  --image gcr.io/$PROJECT_ID/life-witness-agent-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 3. Accessing the Services
- **Backend API Docs:**  
  Visit the Cloud Run URL for `life-witness-agent-backend` (e.g., `https://life-witness-agent-backend-xxxxxx.a.run.app/docs`).
- **Frontend App:**  
  Visit the Cloud Run URL for `life-witness-agent-frontend` (e.g., `https://life-witness-agent-frontend-xxxxxx.a.run.app`).

---

## 4. Environment Variables
- **Frontend:**  
  Set `NEXT_PUBLIC_AGENT_API_URL` in `.env.local` to your backend Cloud Run URL.
- **Backend:**  
  Use environment variables or Google Secret Manager for sensitive data if needed.

---

## 5. Troubleshooting
- **500 Internal Server Error:**  
  Ensure all Python dependencies are installed and your backend code is correct.
- **Memory Issues:**  
  Increase memory allocation with `--memory 1Gi` or higher in the deploy command.
- **.env.local not found:**  
  Make sure it’s present in `frontend/` and not listed in `.dockerignore`.

---

## 6. Useful Commands
- **List Cloud Run services:**
  ```sh
  gcloud run services list --region us-central1 --platform managed
  ```
- **Get service URL:**
  ```sh
  gcloud run services describe SERVICE_NAME --region us-central1 --platform managed --format 'value(status.url)'
  ```

---

## 7. Updating Services
After code changes, repeat the build and deploy steps for the affected service.

---

## 8. Running Deployment Scripts

### a. Local Development
To run both backend and frontend locally using Docker Compose:

```sh
cd agents-assemble
# Start both services
docker-compose up --build
```

Or, to use the provided demo script:
```sh
cd agents-assemble/scripts
./setup_dev.sh   # Set up Python environment and install backend dependencies
./run_demo.sh    # Start the FastAPI backend locally
```

### b. Cloud Deployment
To build and deploy both backend and frontend to Google Cloud Run using the provided script:

```sh
cd agents-assemble/scripts
./deploy.sh
```

This will build Docker images and deploy both services to Cloud Run. Make sure you have authenticated with `gcloud` and set your project.

---

For advanced topics (custom domains, load balancer, etc.), see Google Cloud Run documentation.
