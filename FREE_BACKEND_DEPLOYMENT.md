# Free Backend Deployment Guide - Recipe AI App

## 🆓 Overview
This guide shows you how to deploy your Recipe AI backend **completely FREE** using various free hosting platforms. No credit card required for most options!

**Free Hosting Options:**
1. **Railway** (Recommended) - 5GB storage, 500 hours/month
2. **Render** - 750 hours/month free
3. **Fly.io** - 3 shared-cpu-1x VMs free
4. **Google Cloud Run** - 2 million requests/month free
5. **Heroku Alternative** - Using free tiers

---

## 🚀 Option 1: Railway (Recommended - Easiest)

### Why Railway?
- ✅ **Completely FREE** - No credit card required
- ✅ **Easy deployment** - Connect GitHub and deploy
- ✅ **Automatic HTTPS** - SSL certificates included
- ✅ **Environment variables** - Easy to configure
- ✅ **Logs & monitoring** - Built-in dashboard

### Step 1: Prepare Your Code
```bash
# Navigate to your project
cd "recipe-ai-app"

# Create a simple startup script for Railway
cat > backend/start.sh << 'EOF'
#!/bin/bash
cd /app
python run.py
EOF

# Make it executable
chmod +x backend/start.sh
```

### Step 2: Create Railway Account
1. Go to [Railway.app](https://railway.app)
2. Click **"Start a New Project"**
3. Sign up with **GitHub** (free, no credit card needed)
4. Verify your email

### Step 3: Deploy from GitHub
1. Push your code to GitHub (if not already done):
```bash
# Initialize git (if not done)
git init
git add .
git commit -m "Initial commit"

# Create GitHub repo and push
git remote add origin https://github.com/yourusername/recipe-ai-app.git
git branch -M main
git push -u origin main
```

2. In Railway dashboard:
   - Click **"Deploy from GitHub repo"**
   - Select your repository
   - Choose **"Deploy Now"**

### Step 4: Configure Environment Variables
1. In Railway dashboard, go to your project
2. Click **"Variables"** tab
3. Add these environment variables:

```
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY=your-firebase-private-key
FIREBASE_CLIENT_EMAIL=your-firebase-client-email
OPENAI_API_KEY=sk-your-openai-api-key
NODE_ENV=production
PORT=8000
CORS_ORIGINS=*
```

### Step 5: Configure Deployment Settings
1. Go to **"Settings"** tab
2. Set **"Root Directory"** to `backend`
3. Set **"Build Command"** to `pip install -r requirements.txt`
4. Set **"Start Command"** to `python run.py`

### Step 6: Test Your Deployment
- Railway will provide a URL like: `https://your-app-name.railway.app`
- Test: `https://your-app-name.railway.app/health`

---

## 🚀 Option 2: Render (Also Great)

### Why Render?
- ✅ **750 hours/month free** - Enough for most projects
- ✅ **No credit card** required for free tier
- ✅ **Auto-deploy** from Git
- ✅ **Custom domains** supported

### Step 1: Create Render Account
1. Go to [Render.com](https://render.com)
2. Sign up with **GitHub** (free)
3. No credit card required

### Step 2: Create Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Choose your repo and branch

### Step 3: Configure Service
- **Name**: `recipe-ai-backend`
- **Environment**: `Python 3`
- **Region**: `Ohio` (or closest to you)
- **Branch**: `main`
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python run.py`

### Step 4: Set Environment Variables
Add the same environment variables as Railway:
```
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY=your-firebase-private-key
FIREBASE_CLIENT_EMAIL=your-firebase-client-email
OPENAI_API_KEY=sk-your-openai-api-key
NODE_ENV=production
PORT=10000
CORS_ORIGINS=*
```

### Step 5: Deploy
- Click **"Create Web Service"**
- Wait for deployment (5-10 minutes)
- Your app will be at: `https://your-app-name.onrender.com`

---

## 🚀 Option 3: Fly.io (Developer Friendly)

### Why Fly.io?
- ✅ **3 shared VMs free** - Good for small apps
- ✅ **Global deployment** - Fast worldwide
- ✅ **Dockerfile support** - Use existing Docker setup

### Step 1: Install Fly CLI
```bash
# Mac
brew install flyctl

# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex

# Linux
curl -L https://fly.io/install.sh | sh
```

### Step 2: Sign Up & Login
```bash
# Sign up (no credit card required for free tier)
fly auth signup

# Login
fly auth login
```

### Step 3: Initialize App
```bash
# Navigate to backend folder
cd recipe-ai-app/backend

# Initialize Fly app
fly launch --no-deploy

# Follow prompts:
# - App name: recipe-ai-backend
# - Region: choose closest to you
# - Don't deploy yet: N
```

### Step 4: Configure fly.toml
Edit the generated `fly.toml` file:
```toml
app = "recipe-ai-backend"
primary_region = "dfw"

[build]
  dockerfile = "../deployment/docker/Dockerfile.backend"

[env]
  NODE_ENV = "production"
  PORT = "8080"

[[services]]
  internal_port = 8080
  protocol = "tcp"

  [[services.ports]]
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443
```

### Step 5: Set Secrets (Environment Variables)
```bash
# Set environment variables as secrets
fly secrets set FIREBASE_PROJECT_ID="your-project-id"
fly secrets set FIREBASE_PRIVATE_KEY="your-private-key"
fly secrets set FIREBASE_CLIENT_EMAIL="your-client-email"
fly secrets set OPENAI_API_KEY="sk-your-openai-key"
fly secrets set CORS_ORIGINS="*"
```

### Step 6: Deploy
```bash
# Deploy your app
fly deploy

# Your app will be at: https://recipe-ai-backend.fly.dev
```

---

## 🚀 Option 4: Google Cloud Run (Free Tier)

### Why Google Cloud Run Free Tier?
- ✅ **2 million requests/month** free
- ✅ **180,000 vCPU-seconds** free
- ✅ **360,000 GiB-seconds** memory free
- ✅ **1 GB network egress** free per month

### Free Tier Limits:
- Perfect for development and small projects
- No credit card required if you stay within limits
- Automatic scaling to zero (no cost when not used)

### Step 1: Create Google Account (Free)
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Sign up with regular Google account
3. **Skip billing setup** for now (use free tier)

### Step 2: Create Project
1. Create new project (free)
2. Enable Cloud Run API (free)

### Step 3: Use Cloud Shell (Free)
1. Click **Cloud Shell** icon in top right
2. This gives you a free Linux environment with all tools installed

### Step 4: Deploy Using Cloud Shell
```bash
# In Cloud Shell, clone your repo
git clone https://github.com/yourusername/recipe-ai-app.git
cd recipe-ai-app/backend

# Build and deploy (all free within limits)
gcloud run deploy recipe-ai-backend \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 1
```

---

## 🔧 Free Firebase & OpenAI Setup

### Firebase (Free Tier)
- ✅ **Spark Plan** - Completely free
- ✅ **50,000 reads/day** - Free
- ✅ **20,000 writes/day** - Free
- ✅ **1 GB storage** - Free
- ✅ **10 GB bandwidth** - Free

### OpenAI (Pay-per-use, but cheap)
- 💰 **$5 minimum** - But lasts long time
- 💡 **Alternative**: Use **Google Gemini API** (has free tier)
- 💡 **Alternative**: Use **Anthropic Claude** (has free tier)

### Free OpenAI Alternative - Gemini API
```bash
# Replace OpenAI with free Gemini API
# 1. Go to https://makersuite.google.com/app/apikey
# 2. Create free API key
# 3. Update your environment variables:
GEMINI_API_KEY=your-free-gemini-key
# 4. Modify your backend code to use Gemini instead
```

---

## 📊 Free Tier Comparison

| Platform | Storage | Bandwidth | Uptime | Ease | Best For |
|----------|---------|-----------|--------|------|----------|
| **Railway** | 5GB | Unlimited | 500hrs/mo | ⭐⭐⭐⭐⭐ | Beginners |
| **Render** | 1GB | 100GB/mo | 750hrs/mo | ⭐⭐⭐⭐ | General use |
| **Fly.io** | 3GB | 160GB/mo | Always on | ⭐⭐⭐ | Developers |
| **Cloud Run** | 1GB | 1GB/mo | Pay-per-use | ⭐⭐ | Google users |

---

## 🛠️ Step-by-Step: Railway Deployment (Easiest)

### Complete Railway Setup (10 minutes)

1. **Prepare Repository**
```bash
cd "recipe-ai-app"

# Create Procfile for Railway
echo "web: cd backend && python run.py" > Procfile

# Create railway.json config
cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "cd backend && python run.py",
    "healthcheckPath": "/health"
  }
}
EOF

# Commit changes
git add .
git commit -m "Add Railway configuration"
git push
```

2. **Deploy to Railway**
   - Go to [railway.app](https://railway.app)
   - Click "Start a New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Wait 2-3 minutes for deployment

3. **Configure Environment Variables**
   - In Railway dashboard, click "Variables"
   - Add all your environment variables
   - Click "Deploy" to restart with new variables

4. **Test Your Deployment**
   - Railway provides URL: `https://your-app.railway.app`
   - Test: `https://your-app.railway.app/health`

### Done! Your backend is live and free! 🎉

---

## 💡 Pro Tips for Free Hosting

### 1. Keep Costs Down
- Use **environment variables** instead of config files
- **Optimize your code** - free tiers have resource limits
- **Monitor usage** - stay within free tier limits
- **Use caching** - reduce API calls

### 2. Free Monitoring
- **Railway**: Built-in logs and metrics
- **Render**: Free monitoring dashboard
- **Fly.io**: Built-in metrics
- **UptimeRobot**: Free uptime monitoring (external)

### 3. Free SSL & Custom Domains
- All platforms provide **free HTTPS**
- Most support **custom domains** on free tier
- Use **Cloudflare** for additional free CDN

### 4. Free Database Alternatives
Instead of paid Firebase, consider:
- **Supabase** - Free PostgreSQL (500MB)
- **PlanetScale** - Free MySQL (5GB)
- **MongoDB Atlas** - Free (512MB)
- **Firebase Firestore** - Free tier (1GB)

---

## 🔍 Troubleshooting Free Deployments

### Railway Issues
```bash
# Check build logs in Railway dashboard
# Common fixes:
# 1. Ensure requirements.txt is in backend folder
# 2. Set correct start command: "cd backend && python run.py"
# 3. Set PORT environment variable to match Railway's PORT
```

### Render Issues
```bash
# Check deploy logs in Render dashboard
# Common fixes:
# 1. Set Python version in requirements.txt: python-3.11.0
# 2. Ensure all dependencies are listed
# 3. Check that PORT=10000 (Render's default)
```

### General Issues
- **Build failures**: Check Python version compatibility
- **Module not found**: Ensure all imports are in requirements.txt
- **Port issues**: Use environment PORT variable
- **Environment variables**: Double-check all values are set correctly

---

## ✅ Free Deployment Checklist

### Pre-Deployment
- [ ] Code pushed to GitHub
- [ ] requirements.txt updated
- [ ] Environment variables prepared
- [ ] Firebase free tier configured
- [ ] Free hosting platform account created

### Deployment
- [ ] Repository connected to hosting platform
- [ ] Build configuration set correctly
- [ ] Environment variables configured
- [ ] Health check endpoint working
- [ ] Custom domain configured (optional)

### Post-Deployment
- [ ] Health endpoint responds correctly
- [ ] API endpoints working
- [ ] Frontend can connect to backend
- [ ] Monitoring set up
- [ ] Usage within free tier limits

---

## 🎉 Congratulations!

Your backend is now deployed **completely FREE**! 

**Your free backend URLs:**
- Railway: `https://your-app.railway.app`
- Render: `https://your-app.onrender.com`
- Fly.io: `https://your-app.fly.dev`
- Cloud Run: `https://your-app.run.app`

**Next Steps:**
1. Test all API endpoints
2. Configure frontend to use your free backend URL
3. Set up monitoring to stay within free limits
4. Consider upgrading only when you need more resources

**Free Tier Monitoring:**
- Check usage dashboards regularly
- Set up alerts for approaching limits
- Optimize code to use fewer resources

Your Recipe AI app is now running in the cloud for **$0/month**! 🚀 