# Complete Backend Deployment Guide for Beginners

## 🎯 Overview
This guide will walk you through deploying your Recipe AI backend to Google Cloud Run. We'll go step-by-step, assuming you have no prior experience with cloud deployment.

**What we'll accomplish:**
- Set up Google Cloud Platform account
- Install required tools
- Configure Firebase
- Get OpenAI API key
- Deploy your backend to the cloud
- Test the deployment

**Time required:** 45-60 minutes

---

## 📋 Step 1: Create Google Cloud Platform Account

### 1.1 Sign Up for Google Cloud
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click **"Get started for free"**
3. Sign in with your Google account (create one if needed)
4. **Important:** You'll need to add a credit card, but Google gives you $300 in free credits
5. Complete the signup process

### 1.2 Create a New Project
1. In the Google Cloud Console, click the project dropdown (top left)
2. Click **"New Project"**
3. Enter project name: `recipe-ai-app` (or your preferred name)
4. Click **"Create"**
5. **Write down your Project ID** - you'll need this later!

### 1.3 Enable Billing
1. Go to **Billing** in the left sidebar
2. Link your project to a billing account
3. Don't worry - the free tier covers most development needs

---

## 📋 Step 2: Set Up Firebase

### 2.1 Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Click **"Create a project"**
3. Enter the same project name: `recipe-ai-app`
4. **Important:** Choose **"Use an existing Google Cloud Platform project"**
5. Select the project you created in Step 1
6. Continue through the setup (accept terms, etc.)

### 2.2 Enable Authentication
1. In Firebase Console, click **"Authentication"** in left sidebar
2. Click **"Get started"**
3. Go to **"Sign-in method"** tab
4. Enable **"Email/Password"**
5. Enable **"Google"** (optional but recommended)

### 2.3 Enable Firestore Database
1. Click **"Firestore Database"** in left sidebar
2. Click **"Create database"**
3. Choose **"Start in test mode"** (we'll secure it later)
4. Choose a location (use default or closest to you)

### 2.4 Generate Service Account Key
1. Click the gear icon ⚙️ next to "Project Overview"
2. Click **"Project settings"**
3. Go to **"Service accounts"** tab
4. Click **"Generate new private key"**
5. Click **"Generate key"** - this downloads a JSON file
6. **IMPORTANT:** Save this file securely - you'll need it later!
7. **Never share this file publicly!**

---

## 📋 Step 3: Get OpenAI API Key

### 3.1 Create OpenAI Account
1. Go to [OpenAI Platform](https://platform.openai.com)
2. Sign up for an account
3. Verify your email

### 3.2 Add Payment Method
1. Go to **"Billing"** in your OpenAI dashboard
2. Add a payment method (required for API access)
3. Add some credits ($5-10 is enough for testing)

### 3.3 Create API Key
1. Go to **"API Keys"** section
2. Click **"Create new secret key"**
3. Give it a name: `recipe-ai-backend`
4. **Copy and save this key securely** - you can't see it again!
5. It should start with `sk-`

---

## 📋 Step 4: Install Required Tools

### 4.1 Install Google Cloud SDK (Command Line Tools)

#### For Mac:
```bash
# Open Terminal (press Cmd+Space, type "Terminal")
# Install Homebrew first (if you don't have it)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Google Cloud SDK
brew install google-cloud-sdk
```

#### For Windows:
1. Download the installer from [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
2. Run the installer
3. Follow the setup wizard
4. When prompted, check "Run gcloud init"

#### For Linux:
```bash
# Add the Cloud SDK distribution URI as a package source
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

# Import the Google Cloud public key
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -

# Update and install the Cloud SDK
sudo apt-get update && sudo apt-get install google-cloud-sdk
```

### 4.2 Install Docker

#### For Mac:
1. Download [Docker Desktop for Mac](https://docs.docker.com/desktop/mac/install/)
2. Install the .dmg file
3. Start Docker Desktop
4. Wait for it to finish starting (whale icon in menu bar)

#### For Windows:
1. Download [Docker Desktop for Windows](https://docs.docker.com/desktop/windows/install/)
2. Install the .exe file
3. Restart your computer if prompted
4. Start Docker Desktop

#### For Linux (Ubuntu):
```bash
# Update package index
sudo apt-get update

# Install Docker
sudo apt-get install docker.io

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (to run without sudo)
sudo usermod -aG docker $USER
# Log out and log back in for this to take effect
```

### 4.3 Verify Installations
```bash
# Test Google Cloud SDK
gcloud --version

# Test Docker
docker --version

# If either fails, restart your terminal and try again
```

---

## 📋 Step 5: Configure Your Local Environment

### 5.1 Login to Google Cloud
```bash
# Open Terminal/Command Prompt
# Login to Google Cloud
gcloud auth login

# This will open a browser window
# Sign in with the same Google account you used for Google Cloud
```

### 5.2 Set Your Project
```bash
# Replace YOUR_PROJECT_ID with the Project ID from Step 1.2
gcloud config set project YOUR_PROJECT_ID

# Verify it's set correctly
gcloud config get-value project
```

### 5.3 Enable Required APIs
```bash
# Enable the APIs we need for deployment
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# This might take a few minutes
```

---

## 📋 Step 6: Prepare Your Environment Variables

### 6.1 Navigate to Your Project
```bash
# Navigate to your project folder
cd "recipe-ai-app"

# Verify you're in the right place
ls -la
# You should see folders like: backend, frontend, deployment
```

### 6.2 Create Environment File
```bash
# Navigate to backend folder
cd backend

# Create production environment file
touch .env.production

# Open the file in a text editor
# On Mac: open -e .env.production
# On Windows: notepad .env.production
# On Linux: nano .env.production
```

### 6.3 Fill in Environment Variables
Copy this template into your `.env.production` file and replace the values:

```bash
# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id-here
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nPASTE_YOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# App Configuration
NODE_ENV=production
CORS_ORIGINS=*
PORT=8080
```

**How to fill this out:**

1. **FIREBASE_PROJECT_ID**: Use your project ID from Step 1.2
2. **FIREBASE_PRIVATE_KEY**: 
   - Open the JSON file you downloaded in Step 2.4
   - Find the "private_key" field
   - Copy the entire value (including the quotes)
   - Replace the newlines (\n) with actual line breaks
3. **FIREBASE_CLIENT_EMAIL**:
   - From the same JSON file, copy the "client_email" value
4. **OPENAI_API_KEY**: Use the key from Step 3.3

---

## 📋 Step 7: Build and Deploy

### 7.1 Test Docker is Running
```bash
# Make sure Docker is running
docker info

# If you get an error, start Docker Desktop and wait for it to fully load
```

### 7.2 Build the Docker Image
```bash
# Make sure you're in the backend folder
pwd
# Should show: /path/to/recipe-ai-app/backend

# Build the Docker image (replace YOUR_PROJECT_ID)
docker build -f ../deployment/docker/Dockerfile.backend -t gcr.io/YOUR_PROJECT_ID/recipe-ai-backend:latest .

# This will take several minutes the first time
# You'll see lots of output - this is normal!
```

### 7.3 Push to Google Container Registry
```bash
# Configure Docker to use gcloud as a credential helper
gcloud auth configure-docker

# Push the image to Google Container Registry
docker push gcr.io/YOUR_PROJECT_ID/recipe-ai-backend:latest

# This will take a few minutes to upload
```

### 7.4 Deploy to Cloud Run
```bash
# Deploy to Cloud Run (replace YOUR_PROJECT_ID)
gcloud run deploy recipe-ai-backend \
    --image gcr.io/YOUR_PROJECT_ID/recipe-ai-backend:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --concurrency 80 \
    --max-instances 10 \
    --port 8080 \
    --timeout 300

# When prompted:
# - Allow unauthenticated invocations? Y
# - Service will be deployed to us-central1
```

### 7.5 Set Environment Variables in Cloud Run
```bash
# Set your environment variables (replace with your actual values)
gcloud run services update recipe-ai-backend \
    --region us-central1 \
    --set-env-vars "FIREBASE_PROJECT_ID=your-project-id,NODE_ENV=production,PORT=8080" \
    --set-env-vars "OPENAI_API_KEY=sk-your-openai-key" \
    --set-env-vars "FIREBASE_CLIENT_EMAIL=your-firebase-email" \
    --set-env-vars "FIREBASE_PRIVATE_KEY=your-private-key-here"

# Note: For the private key, you might need to set it through the web console instead
```

---

## 📋 Step 8: Set Environment Variables via Web Console (Recommended)

### 8.1 Open Cloud Run Console
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **Cloud Run** (search for it in the top search bar)
3. Click on your **recipe-ai-backend** service

### 8.2 Edit Service
1. Click **"Edit & Deploy New Revision"**
2. Go to **"Variables & Secrets"** tab
3. Click **"Add Variable"** for each environment variable:

**Add these variables one by one:**
- Name: `FIREBASE_PROJECT_ID`, Value: `your-project-id`
- Name: `NODE_ENV`, Value: `production`
- Name: `PORT`, Value: `8080`
- Name: `OPENAI_API_KEY`, Value: `sk-your-openai-key`
- Name: `FIREBASE_CLIENT_EMAIL`, Value: `your-firebase-email`
- Name: `FIREBASE_PRIVATE_KEY`, Value: `your-private-key` (paste the full key with line breaks)

4. Click **"Deploy"**

---

## 📋 Step 9: Test Your Deployment

### 9.1 Get Your Service URL
```bash
# Get the URL of your deployed service
gcloud run services describe recipe-ai-backend --region us-central1 --format 'value(status.url)'

# Copy this URL - you'll need it!
```

### 9.2 Test the Health Endpoint
```bash
# Test your deployment (replace with your actual URL)
curl https://your-service-url.run.app/health

# You should see something like:
# {"status": "healthy", "timestamp": "2024-01-01T12:00:00Z"}
```

### 9.3 Test in Browser
1. Open your browser
2. Go to: `https://your-service-url.run.app/health`
3. You should see the health check response

---

## 🔍 Troubleshooting Common Issues

### Issue 1: "Address already in use" Error
```bash
# If you see this error when testing locally:
# Kill any processes using port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
export PORT=8080
python run.py
```

### Issue 2: Docker Build Fails
```bash
# Make sure Docker is running
docker info

# If Docker isn't running:
# - On Mac/Windows: Start Docker Desktop
# - On Linux: sudo systemctl start docker

# Try building again
docker build -f ../deployment/docker/Dockerfile.backend -t gcr.io/YOUR_PROJECT_ID/recipe-ai-backend:latest .
```

### Issue 3: Permission Denied
```bash
# If you get permission errors with gcloud:
gcloud auth login

# If you get Docker permission errors on Linux:
sudo usermod -aG docker $USER
# Then log out and log back in
```

### Issue 4: Environment Variables Not Working
1. Go to Cloud Run Console
2. Edit your service
3. Check that all environment variables are set correctly
4. Make sure there are no extra spaces or quotes
5. Deploy a new revision

### Issue 5: Service Won't Start
```bash
# Check the logs
gcloud logs tail --service=recipe-ai-backend

# Common issues:
# - Missing environment variables
# - Incorrect Firebase credentials
# - Invalid OpenAI API key
```

---

## 📊 Monitoring Your Deployment

### View Logs
```bash
# View real-time logs
gcloud logs tail --service=recipe-ai-backend

# View recent logs
gcloud logs read --service=recipe-ai-backend --limit=50
```

### Monitor Performance
1. Go to [Cloud Run Console](https://console.cloud.google.com/run)
2. Click on your service
3. Go to **"Metrics"** tab to see:
   - Request count
   - Response time
   - Error rate
   - CPU/Memory usage

---

## ✅ Success Checklist

- [ ] Google Cloud project created and billing enabled
- [ ] Firebase project configured with Authentication and Firestore
- [ ] OpenAI API key obtained and credits added
- [ ] Google Cloud SDK installed and configured
- [ ] Docker installed and running
- [ ] Environment variables file created
- [ ] Docker image built successfully
- [ ] Image pushed to Container Registry
- [ ] Service deployed to Cloud Run
- [ ] Environment variables set in Cloud Run
- [ ] Health endpoint returns successful response
- [ ] Service URL saved for frontend configuration

---

## 🎉 Congratulations!

Your backend is now deployed to Google Cloud Run! 

**Your backend URL:** `https://your-service-url.run.app`

**Next Steps:**
1. Save your service URL - you'll need it for frontend deployment
2. Test all API endpoints
3. Configure your frontend to use this backend URL
4. Set up monitoring and alerts

**Important URLs to bookmark:**
- Your backend: `https://your-service-url.run.app`
- Health check: `https://your-service-url.run.app/health`
- Google Cloud Console: `https://console.cloud.google.com`
- Cloud Run Console: `https://console.cloud.google.com/run`

---

## 💡 Tips for Success

1. **Keep your credentials secure** - Never commit API keys or private keys to Git
2. **Monitor your usage** - Check Google Cloud billing regularly
3. **Test thoroughly** - Always test your deployment before using it in production
4. **Keep backups** - Save your environment variables and configuration files
5. **Update regularly** - Keep your dependencies and Docker images updated

Need help? Check the logs first - most issues are visible there! 