# Quick Deployment Guide

## 🚀 Deploy Your Recipe AI App to Production

### Prerequisites
- Google Cloud account with billing enabled
- Vercel account (free)
- Firebase project with Authentication & Firestore enabled
- OpenAI API key

### 1. Backend Deployment (Google Cloud Run)

```bash
# 1. Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
gcloud init

# 2. Set up your project
gcloud config set project YOUR_PROJECT_ID
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com

# 3. Deploy backend
cd recipe-ai-app/deployment/scripts
chmod +x deploy-backend.sh
./deploy-backend.sh YOUR_PROJECT_ID us-central1
```

**Set these environment variables in Cloud Run:**
- `FIREBASE_PROJECT_ID`: Your Firebase project ID
- `FIREBASE_PRIVATE_KEY`: Your Firebase private key
- `FIREBASE_CLIENT_EMAIL`: Your Firebase client email
- `OPENAI_API_KEY`: Your OpenAI API key
- `NODE_ENV`: production
- `CORS_ORIGINS`: https://your-frontend-domain.vercel.app

### 2. Frontend Deployment (Vercel)

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Deploy frontend
cd recipe-ai-app/deployment/scripts
chmod +x deploy-frontend.sh
./deploy-frontend.sh
```

**Set these environment variables in Vercel:**
- `REACT_APP_API_URL`: Your Cloud Run backend URL
- `REACT_APP_FIREBASE_API_KEY`: Your Firebase web API key
- `REACT_APP_FIREBASE_AUTH_DOMAIN`: your-project.firebaseapp.com
- `REACT_APP_FIREBASE_PROJECT_ID`: Your Firebase project ID
- `REACT_APP_FIREBASE_STORAGE_BUCKET`: your-project.appspot.com
- `REACT_APP_FIREBASE_MESSAGING_SENDER_ID`: Your messaging sender ID
- `REACT_APP_FIREBASE_APP_ID`: Your Firebase app ID

### 3. Test Your Deployment

1. Backend health check: `https://your-backend-url.run.app/health`
2. Frontend: `https://your-app.vercel.app`

### 4. Automatic Deployments (Optional)

Push to GitHub main branch to trigger automatic deployments via GitHub Actions.

**Required GitHub Secrets:**
- `GCP_PROJECT_ID`, `GCP_SA_KEY`
- `VERCEL_TOKEN`, `ORG_ID`, `PROJECT_ID`
- All environment variables

---

Your app is now live! 🎉 