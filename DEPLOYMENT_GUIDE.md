# Complete Deployment Guide - Recipe AI App

## 📋 Prerequisites

Before deploying, ensure you have:

### Required Accounts & Services
- ✅ **Google Cloud Platform** account with billing enabled
- ✅ **Vercel** account (free tier available)
- ✅ **Firebase** project with Authentication & Firestore setup
- ✅ **OpenAI** API key with credits
- ✅ **GitHub** account (optional, for CI/CD)

### Required Tools
- ✅ **Node.js** (v16 or higher)
- ✅ **Python** (v3.8 or higher)
- ✅ **Docker** (for backend deployment)
- ✅ **Git**

---

## 🔧 Pre-Deployment Setup

### 1. Firebase Setup
```bash
# 1. Go to Firebase Console (https://console.firebase.google.com)
# 2. Create a new project or select existing one
# 3. Enable Authentication (Email/Password, Google)
# 4. Enable Firestore Database
# 5. Generate service account key:
#    - Go to Project Settings > Service Accounts
#    - Generate new private key (JSON file)
#    - Save this file securely
```

### 2. OpenAI API Setup
```bash
# 1. Go to OpenAI Platform (https://platform.openai.com)
# 2. Create API key
# 3. Add credits to your account
# 4. Save the API key securely
```

### 3. Google Cloud Setup
```bash
# 1. Go to Google Cloud Console (https://console.cloud.google.com)
# 2. Create new project or select existing one
# 3. Enable billing
# 4. Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

---

## 🚀 Backend Deployment (Google Cloud Run)

### Step 1: Install Dependencies & Setup
```bash
# Navigate to your project
cd recipe-ai-app

# Install Google Cloud SDK (if not already installed)
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Login to Google Cloud
gcloud auth login

# Set your project ID
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### Step 2: Prepare Environment Variables
Create a file `backend/env.production` with your production values:
```bash
# Firebase Configuration
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour-Private-Key-Here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key

# App Configuration
NODE_ENV=production
CORS_ORIGINS=https://your-frontend-domain.vercel.app
PORT=8080
```

### Step 3: Build and Deploy
```bash
# Make deployment script executable
chmod +x deployment/scripts/deploy-backend.sh

# Deploy backend (replace with your actual project ID)
./deployment/scripts/deploy-backend.sh your-project-id us-central1

# Or deploy manually:
cd backend

# Build Docker image
docker build -f ../deployment/docker/Dockerfile.backend -t gcr.io/$PROJECT_ID/recipe-ai-backend:latest .

# Push to Container Registry
docker push gcr.io/$PROJECT_ID/recipe-ai-backend:latest

# Deploy to Cloud Run
gcloud run deploy recipe-ai-backend \
    --image gcr.io/$PROJECT_ID/recipe-ai-backend:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --concurrency 80 \
    --max-instances 10 \
    --port 8080 \
    --timeout 300
```

### Step 4: Configure Environment Variables in Cloud Run
```bash
# Set environment variables in Cloud Run Console
# Or use gcloud command:
gcloud run services update recipe-ai-backend \
    --region us-central1 \
    --set-env-vars "FIREBASE_PROJECT_ID=your-firebase-project-id,OPENAI_API_KEY=sk-your-key,NODE_ENV=production"
```

### Step 5: Test Backend Deployment
```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe recipe-ai-backend --region us-central1 --format 'value(status.url)')

# Test health endpoint
curl $SERVICE_URL/health

# Should return: {"status": "healthy", "timestamp": "..."}
```

---

## 🌐 Frontend Deployment (Vercel)

### Step 1: Install Vercel CLI
```bash
# Install Vercel CLI globally
npm install -g vercel

# Login to Vercel
vercel login
```

### Step 2: Prepare Environment Variables
Create `frontend/.env.production`:
```bash
# Backend API URL (from Cloud Run deployment)
REACT_APP_API_URL=https://your-backend-url.run.app

# Firebase Web Configuration
REACT_APP_FIREBASE_API_KEY=your-web-api-key
REACT_APP_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your-project-id
REACT_APP_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=123456789
REACT_APP_FIREBASE_APP_ID=1:123456789:web:abc123def456
```

### Step 3: Deploy Frontend
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm ci

# Build the project
npm run build

# Deploy to Vercel
vercel --prod

# Or use the deployment script:
cd ../deployment/scripts
chmod +x deploy-frontend.sh
./deploy-frontend.sh
```

### Step 4: Configure Environment Variables in Vercel
```bash
# Option 1: Via Vercel CLI
vercel env add REACT_APP_API_URL production
vercel env add REACT_APP_FIREBASE_API_KEY production
# ... add all other environment variables

# Option 2: Via Vercel Dashboard
# 1. Go to your project in Vercel dashboard
# 2. Go to Settings > Environment Variables
# 3. Add all the environment variables from .env.production
```

### Step 5: Test Frontend Deployment
```bash
# Your frontend should be available at:
# https://your-app-name.vercel.app

# Test the deployment by:
# 1. Opening the URL in browser
# 2. Trying to register/login
# 3. Testing recipe generation
```

---

## 🔄 Automatic Deployments (CI/CD)

### GitHub Actions Setup

#### Step 1: Create GitHub Repository
```bash
# Initialize git repository (if not already done)
git init
git add .
git commit -m "Initial commit"

# Create GitHub repository and push
git remote add origin https://github.com/yourusername/recipe-ai-app.git
git branch -M main
git push -u origin main
```

#### Step 2: Configure GitHub Secrets
Go to your GitHub repository → Settings → Secrets and Variables → Actions

Add these secrets:
```
# Google Cloud
GCP_PROJECT_ID=your-project-id
GCP_SA_KEY={"type": "service_account", "project_id": "..."}

# Vercel
VERCEL_TOKEN=your-vercel-token
VERCEL_ORG_ID=your-org-id
VERCEL_PROJECT_ID=your-project-id

# Environment Variables
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-service-account-email
OPENAI_API_KEY=your-openai-key
REACT_APP_API_URL=your-backend-url
REACT_APP_FIREBASE_API_KEY=your-firebase-web-key
# ... all other environment variables
```

#### Step 3: GitHub Actions Workflow
The workflow files are already created in `.github/workflows/`. They will automatically:
- Deploy backend to Cloud Run on push to main
- Deploy frontend to Vercel on push to main
- Run tests before deployment

---

## 🔍 Troubleshooting

### Common Backend Issues

1. **Container fails to start**
   ```bash
   # Check logs
   gcloud logs tail --service=recipe-ai-backend
   
   # Common fixes:
   # - Verify environment variables are set correctly
   # - Check Firebase service account key format
   # - Ensure OpenAI API key is valid
   ```

2. **Health check fails**
   ```bash
   # Test locally first
   cd backend
   python run.py
   curl http://localhost:8000/health
   ```

3. **CORS errors**
   ```bash
   # Update CORS_ORIGINS environment variable
   gcloud run services update recipe-ai-backend \
       --region us-central1 \
       --set-env-vars "CORS_ORIGINS=https://your-frontend-domain.vercel.app"
   ```

### Common Frontend Issues

1. **Build fails**
   ```bash
   # Check for TypeScript errors
   npm run build
   
   # Fix any compilation errors before deploying
   ```

2. **Environment variables not working**
   ```bash
   # Ensure all REACT_APP_ prefixed variables are set in Vercel
   # Redeploy after adding environment variables
   vercel --prod
   ```

3. **API calls failing**
   ```bash
   # Check browser console for CORS errors
   # Verify REACT_APP_API_URL is correct
   # Test backend health endpoint directly
   ```

---

## 📊 Monitoring & Maintenance

### Backend Monitoring
```bash
# View logs
gcloud logs tail --service=recipe-ai-backend

# Monitor metrics in Cloud Console
# Set up alerting for errors/high latency
```

### Frontend Monitoring
```bash
# Vercel Analytics (available in dashboard)
# Monitor Core Web Vitals
# Set up error tracking (Sentry integration)
```

### Cost Optimization
```bash
# Backend (Cloud Run):
# - Set appropriate CPU/memory limits
# - Configure auto-scaling
# - Monitor usage patterns

# Frontend (Vercel):
# - Optimize bundle size
# - Use CDN for static assets
# - Monitor bandwidth usage
```

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] Firebase project configured
- [ ] OpenAI API key obtained
- [ ] Google Cloud project created
- [ ] All environment variables prepared
- [ ] Local testing completed

### Backend Deployment
- [ ] Docker image builds successfully
- [ ] Cloud Run service deployed
- [ ] Environment variables configured
- [ ] Health check passes
- [ ] API endpoints accessible

### Frontend Deployment
- [ ] Build completes without errors
- [ ] Vercel deployment successful
- [ ] Environment variables set
- [ ] Frontend loads correctly
- [ ] Authentication works
- [ ] API integration functional

### Post-Deployment
- [ ] End-to-end testing completed
- [ ] Monitoring set up
- [ ] CI/CD pipeline configured
- [ ] Documentation updated
- [ ] Team access configured

---

## 🆘 Support

If you encounter issues:

1. **Check the logs** (most issues are visible in logs)
2. **Verify environment variables** (common source of errors)
3. **Test components individually** (backend health, frontend build)
4. **Check service status** (Google Cloud Status, Vercel Status)
5. **Review documentation** (Firebase, OpenAI, Cloud Run, Vercel docs)

---

**🎉 Congratulations! Your Recipe AI App is now live in production!**

Backend: `https://your-backend-url.run.app`
Frontend: `https://your-app.vercel.app` 