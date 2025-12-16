# Vultr Backend Deployment Guide

Deploy your Dealfu backend to Vultr Cloud Compute for the hackathon.

## Quick Deploy (5 minutes)

### Step 1: Create Vultr Cloud Compute Instance

1. Go to https://my.vultr.com/deploy/
2. Choose:
   - **Type**: Cloud Compute - Shared CPU
   - **Location**: Same region as your database (for lowest latency)
   - **Image**: Marketplace → **Docker**
   - **Plan**: $6/mo (1 vCPU, 1GB RAM) - sufficient for demo
3. Add your SSH key
4. Click "Deploy Now"
5. Wait ~2 minutes for server to be ready
6. Copy the IP address

### Step 2: SSH and Deploy

```bash
# SSH into your server
ssh root@YOUR_SERVER_IP

# Clone the repo
git clone https://github.com/YOUR_USERNAME/dealfu.git /opt/dealfu
cd /opt/dealfu/backend

# Create environment file
cat > .env << 'EOF'
# API Keys
CEREBRAS_API_KEY=your_cerebras_key
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID=your_voice_id
RAINDROP_API_KEY=your_raindrop_key

# Vultr PostgreSQL (your managed database)
VULTR_DATABASE_URL=postgresql+asyncpg://vultradmin:PASSWORD@HOST:PORT/defaultdb

# Frontend URL for CORS
PRODUCTION_DOMAIN=https://your-app.vercel.app
EOF

# Edit with your actual values
nano .env

# Build and run
docker build -t dealfu-api .
docker run -d \
  --name dealfu-api \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  dealfu-api

# Verify it's running
curl http://localhost:8000/health
```

### Step 3: Set Up HTTPS with Caddy (Recommended)

```bash
# Install Caddy
apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt update && apt install caddy

# Configure reverse proxy (replace with your domain)
cat > /etc/caddy/Caddyfile << 'EOF'
api.yourdomain.com {
    reverse_proxy localhost:8000
}
EOF

# Or use IP directly (no SSL, for testing)
cat > /etc/caddy/Caddyfile << 'EOF'
:80 {
    reverse_proxy localhost:8000
}
EOF

# Start Caddy
systemctl restart caddy
```

### Step 4: Configure Firewall

```bash
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw --force enable
```

### Step 5: Update Frontend

Update `frontend/.env.production`:
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
# Or for IP: http://YOUR_SERVER_IP:8000
```

Redeploy on Vercel.

---

## Maintenance Commands

```bash
# View logs
docker logs -f dealfu-api

# Restart
docker restart dealfu-api

# Update to latest code
cd /opt/dealfu
git pull
cd backend
docker build -t dealfu-api .
docker stop dealfu-api
docker rm dealfu-api
docker run -d --name dealfu-api -p 8000:8000 --env-file .env --restart unless-stopped dealfu-api

# Check status
docker ps
curl http://localhost:8000/health
```

---

## Alternative: Use deploy.sh Script

```bash
# On your server
cd /opt/dealfu/backend
chmod +x deploy.sh
./deploy.sh
```

---

## Costs

| Service | Cost |
|---------|------|
| Vultr Cloud Compute | $6/mo |
| Vultr Managed PostgreSQL | $15/mo |
| Domain (optional) | ~$12/year |
| **Total** | ~$21-22/mo |

*Use the $500 hackathon credits to cover this!*

---

## Troubleshooting

**Container won't start:**
```bash
docker logs dealfu-api
```

**Database connection fails:**
- Check VULTR_DATABASE_URL format
- Ensure database allows connections from your server IP
- In Vultr DB dashboard → Trusted Sources → Add your server IP

**CORS errors:**
- Verify PRODUCTION_DOMAIN in .env matches your frontend URL exactly
- Include protocol (https://)

**Health check fails:**
```bash
curl -v http://localhost:8000/health
docker logs dealfu-api
```
