# Deployment Guide

Complete guide for deploying Nano Banana MCP Server to various platforms.

## Table of Contents

- [Local Development](#local-development)
- [Docker](#docker)
- [DigitalOcean](#digitalocean)
- [Fly.io](#flyio)
- [Railway](#railway)
- [Render](#render)

---

## Local Development

### STDIO Mode (Cursor Integration)

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python server.py
```

### HTTP Mode (Testing)

```bash
# Run on default port 8000
python server.py --http

# Run on custom port
PORT=3000 python server.py --http
```

---

## Docker

### Build and Run

```bash
# Build image
docker build -t nano-banana-mcp .

# Run container
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your-api-key \
  nano-banana-mcp
```

### Docker Compose

```bash
# Create .env file
echo "GEMINI_API_KEY=your-api-key" > .env

# Start service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

---

## DigitalOcean

### Prerequisites

- DigitalOcean account
- GitHub repo connected
- `doctl` CLI (optional)

### Method 1: One-Click Deploy (Easiest)

1. Click the deploy button:
   
   [![Deploy to DO](https://www.deploytodo.com/do-btn-blue.svg)](https://cloud.digitalocean.com/apps/new?repo=https://github.com/bcharleson/nano-banana-mcp/tree/main)

2. Connect your GitHub account
3. Add `GEMINI_API_KEY` as a secret environment variable
4. Click "Create Resources"

### Method 2: Via Console

1. Go to https://cloud.digitalocean.com/apps
2. Click "Create App"
3. Select "GitHub" as source
4. Choose repository: `bcharleson/nano-banana-mcp`
5. Select branch: `main`
6. DigitalOcean auto-detects `.do/app.yaml` config
7. Add environment variables:
   - `GEMINI_API_KEY` (Secret)
8. Click "Next" → Review → "Create Resources"

### Method 3: Via CLI

```bash
# Install doctl
brew install doctl  # macOS
# or
snap install doctl  # Linux

# Authenticate
doctl auth init

# Create app from spec
doctl apps create --spec .do/app.yaml

# Get app ID
doctl apps list

# Update app with secrets
doctl apps update YOUR_APP_ID \
  --env GEMINI_API_KEY=your-api-key

# View logs
doctl apps logs YOUR_APP_ID --follow

# Get app URL
doctl apps get YOUR_APP_ID
```

### Monitoring

```bash
# Check deployment status
doctl apps get YOUR_APP_ID

# View logs
doctl apps logs YOUR_APP_ID --follow --type=run

# Check health
curl https://your-app-url.ondigitalocean.app/health
```

### Updating

**Via GitHub:**
- Push to `main` branch
- Auto-deploys via webhook

**Via CLI:**
```bash
doctl apps update YOUR_APP_ID --spec .do/app.yaml
```

### Scaling

Edit `.do/app.yaml`:
```yaml
services:
  - name: web
    instance_count: 3  # Scale to 3 instances
    instance_size_slug: basic-xs  # Upgrade to 1GB RAM
```

Then update:
```bash
doctl apps update YOUR_APP_ID --spec .do/app.yaml
```

### Pricing

- **Basic XXS**: $5/month (512MB RAM, 1 vCPU)
- **Basic XS**: $12/month (1GB RAM, 1 vCPU)
- **Basic S**: $24/month (2GB RAM, 2 vCPU)

---

## Fly.io

### Prerequisites

- Fly.io account
- `flyctl` CLI

### Deploy

```bash
# Install flyctl
brew install flyctl

# Login
flyctl auth login

# Launch app (first time)
flyctl launch

# Set secrets
flyctl secrets set GEMINI_API_KEY=your-api-key

# Deploy
flyctl deploy

# Open app
flyctl open

# View logs
flyctl logs
```

### Custom Domain

```bash
flyctl certs add your-domain.com
flyctl ips list
```

---

## Railway

### Method 1: Deploy Button

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/bcharleson/nano-banana-mcp)

### Method 2: Via CLI

```bash
# Install railway CLI
npm install -g @railway/cli

# Login
railway login

# Init project
railway init

# Add variables
railway variables set GEMINI_API_KEY=your-api-key

# Deploy
railway up

# Open app
railway open
```

---

## Render

### Via Dashboard

1. Go to https://render.com
2. Click "New" → "Web Service"
3. Connect GitHub repo
4. Configure:
   - **Name**: nano-banana-mcp
   - **Environment**: Docker
   - **Region**: Choose closest
   - **Instance Type**: Free or Starter ($7/month)
5. Add environment variable:
   - `GEMINI_API_KEY`: your-api-key
6. Click "Create Web Service"

### Via CLI

```bash
# Install render CLI
brew tap render-oss/render
brew install render

# Login
render login

# Deploy
render deploy
```

---

## Environment Variables

All platforms require:

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ | Your Gemini API key |
| `PORT` | ❌ | HTTP port (default: 8000) |

---

## Connecting to Deployed Server

Once deployed, update `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "nano-banana-remote": {
      "url": "https://your-app-url.com"
    }
  }
}
```

Replace `your-app-url.com` with your actual deployment URL:
- **DigitalOcean**: `your-app.ondigitalocean.app`
- **Fly.io**: `your-app.fly.dev`
- **Railway**: `your-app.up.railway.app`
- **Render**: `your-app.onrender.com`

---

## Troubleshooting

### Health Check Fails

```bash
# Test health endpoint
curl https://your-app-url.com/health

# Should return: OK
```

### Image Generation Timeout

Increase timeout in platform settings:
- **DigitalOcean**: Edit `.do/app.yaml` → `timeout_seconds`
- **Fly.io**: Edit `fly.toml` → `http_service.timeout`

### Out of Memory

Upgrade instance size:
- **DigitalOcean**: Change `instance_size_slug` in `.do/app.yaml`
- **Fly.io**: Run `flyctl scale vm shared-cpu-2x --memory 1024`

### API Key Not Working

Verify secret is set:
```bash
# DigitalOcean
doctl apps spec get YOUR_APP_ID

# Fly.io
flyctl secrets list

# Railway
railway variables
```

---

## Performance Tips

1. **Use CDN**: Enable CDN on your platform for faster image delivery
2. **Cache Images**: Store generated images in object storage (S3, Spaces)
3. **Rate Limiting**: Implement rate limiting for public deployments
4. **Monitoring**: Set up alerts for errors and high latency

---

## Security

1. **Never commit** `.env` files
2. **Use secrets** for `GEMINI_API_KEY`
3. **Enable HTTPS** (automatic on most platforms)
4. **Add authentication** for public deployments
5. **Monitor usage** to prevent abuse

---

## Support

- **Issues**: https://github.com/bcharleson/nano-banana-mcp/issues
- **Discussions**: https://github.com/bcharleson/nano-banana-mcp/discussions
- **X/Twitter**: [@brandoncharleson](https://x.com/brandoncharleson)
