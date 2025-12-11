# Vultr Deployment Guide

## Prerequisites
- Vultr account (https://vultr.com)
- Domain name (optional but recommended)

## Step 1: Create Vultr Instance

1. Log into Vultr Dashboard
2. Click "Deploy New Server"
3. Choose:
   - **Type**: Cloud Compute (Shared CPU)
   - **Location**: Choose closest to your users
   - **Image**: Marketplace → Docker (or Ubuntu 22.04)
   - **Plan**: $6/mo (1 vCPU, 1GB RAM) - sufficient for MVP
4. Add your SSH key for secure access
5. Click "Deploy Now"

## Step 2: Initial Server Setup

SSH into your server:
```bash
ssh root@YOUR_SERVER_IP
```

If you chose Ubuntu instead of Docker image:
```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
```

## Step 3: Deploy the Application

```bash
# Download deploy script
curl -O https://raw.githubusercontent.com/radebe49/objection-dojo/main/backend/deploy.sh
chmod +x deploy.sh

# Run first-time setup
./deploy.sh
```

Create your environment file:
```bash
nano /opt/objection-dojo/backend/.env
```

Add your API keys:
```
CEREBRAS_API_KEY=your_cerebras_key
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID=your_voice_id
RAINDROP_API_KEY=your_raindrop_key
PRODUCTION_DOMAIN=https://objection-dojo.vercel.app
```

Run deployment:
```bash
./deploy.sh
```

## Step 4: Set Up Domain & SSL (Recommended)

Install Caddy for automatic HTTPS:
```bash
apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt update
apt install caddy
```

Configure Caddy:
```bash
nano /etc/caddy/Caddyfile
```

Add:
```
api.yourdomain.com {
    reverse_proxy localhost:8000
}
```

Restart Caddy:
```bash
systemctl restart caddy
```

## Step 5: Update Frontend

Update `frontend/.env.production`:
```
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

Redeploy frontend on Vercel.

## Maintenance Commands

```bash
# View logs
docker logs -f objection-dojo-api

# Restart
docker restart objection-dojo-api

# Update to latest
cd /opt/objection-dojo && ./backend/deploy.sh

# Check status
docker ps
curl http://localhost:8000/health
```

## Firewall Setup

```bash
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable
```

## Estimated Costs

- Vultr Cloud Compute: $6-12/mo
- Domain: ~$12/year
- Total: ~$7-13/mo
