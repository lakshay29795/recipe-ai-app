#!/bin/bash

# Deploy Frontend to Vercel
# Usage: ./deploy-frontend.sh

set -e

echo "🚀 Deploying Recipe AI Frontend to Vercel..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI is not installed. Installing..."
    npm install -g vercel
fi

# Navigate to frontend directory
cd ../../frontend

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found. Make sure you're in the frontend directory."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm ci

# Build the project
echo "🏗️ Building project..."
npm run build

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
vercel --prod

echo "✅ Frontend deployment completed!"
echo "🌐 Your app should be available at the URL shown above"
echo "⚙️ Configure environment variables in Vercel dashboard if needed" 