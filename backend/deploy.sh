#!/bin/bash
# Dealfu Backend - Vultr Deployment Script
# Run this on your Vultr Cloud Compute instance

set -e

APP_NAME="dealfu-api"
APP_DIR="/opt/objection-dojo"
REPO_URL="https://github.com/radebe49/projectsalesdojo.git"

echo "🚀 Deploying $APP_NAME..."

# Check if first-time setup
if [ ! -d "$APP_DIR" ]; then
    echo "📦 First-time setup - cloning repository..."
    git clone "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR/backend"
    
    echo "⚠️  Create your .env file with API keys:"
    echo "    nano $APP_DIR/backend/.env"
    echo ""
    echo "Required variables:"
    echo "  CEREBRAS_API_KEY=your_key"
    echo "  ELEVENLABS_API_KEY=your_key"
    echo "  ELEVENLABS_VOICE_ID=your_voice_id"
    echo "  RAINDROP_API_KEY=your_key"
    echo "  PRODUCTION_DOMAIN=https://your-frontend-domain.vercel.app"
    echo ""
    echo "Then run this script again."
    exit 0
fi

cd "$APP_DIR/backend"

# Check for .env file
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "   Create it with: nano $APP_DIR/backend/.env"
    exit 1
fi

echo "📥 Pulling latest changes..."
git pull origin main

echo "🔨 Building Docker image..."
docker build -t "$APP_NAME" .

echo "🛑 Stopping existing container (if any)..."
docker stop "$APP_NAME" 2>/dev/null || true
docker rm "$APP_NAME" 2>/dev/null || true

echo "🚀 Starting new container..."
docker run -d \
    --name "$APP_NAME" \
    -p 8000:8000 \
    --env-file .env \
    --restart unless-stopped \
    "$APP_NAME"

echo "⏳ Waiting for health check..."
sleep 5

# Health check
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ Deployment successful! API is running at http://localhost:8000"
else
    echo "❌ Health check failed. Check logs with: docker logs $APP_NAME"
    exit 1
fi

echo ""
echo "📋 Useful commands:"
echo "   View logs:    docker logs -f $APP_NAME"
echo "   Stop:         docker stop $APP_NAME"
echo "   Restart:      docker restart $APP_NAME"
