# Nano Banana Pro MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MCP server for Google Gemini's Nano Banana Pro image generation model (`gemini-3-pro-image-preview`).

Supports both **STDIO** (local Cursor integration) and **HTTP/SSE** (remote deployment) transports.

## Features

- **Text-to-Image Generation**: Create high-fidelity images from text descriptions
- **Image Editing**: Edit existing images with conversational text prompts
- **Multiple Aspect Ratios**: Support for 1:1, 16:9, 9:16, 4:3, 3:4
- **Batch Generation**: Generate up to 4 images at once
- **High Resolution**: 2K-4K output with Nano Banana Pro
- **Dual Transport**: STDIO for local use, HTTP/SSE for remote deployment

## Quick Start

### Prerequisites

- Python 3.11+
- Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

> 📖 **Full Deployment Guide**: See [DEPLOY.md](DEPLOY.md) for detailed deployment instructions for all platforms.

### Installation

```bash
git clone https://github.com/bcharleson/nano-banana-mcp.git
cd nano-banana-mcp
pip install -r requirements.txt
```

### Local Usage (STDIO)

**1. Configure Cursor**

Add to `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "nano-banana": {
      "command": "python3",
      "args": [
        "/absolute/path/to/nano-banana-mcp/server.py"
      ],
      "env": {
        "GEMINI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

**2. Restart Cursor**

The server will be available via MCP tools.

### Remote Deployment (HTTP/SSE)

#### Option 1: Docker

```bash
# Build
docker build -t nano-banana-mcp .

# Run
docker run -p 8000:8000 -e GEMINI_API_KEY=your-api-key nano-banana-mcp
```

#### Option 2: Docker Compose

```bash
# Create .env file
echo "GEMINI_API_KEY=your-api-key" > .env

# Run
docker-compose up -d
```

#### Option 3: Fly.io

```bash
# Install flyctl
brew install flyctl

# Login
flyctl auth login

# Set secret
flyctl secrets set GEMINI_API_KEY=your-api-key

# Deploy
flyctl launch
```

#### Option 4: Railway

1. Click: [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)
2. Add `GEMINI_API_KEY` environment variable
3. Deploy!

#### Option 5: Render

1. Create new Web Service
2. Connect this repo
3. Set environment variable: `GEMINI_API_KEY`
4. Deploy command: `python server.py --http`

#### Option 6: DigitalOcean App Platform

**Via doctl CLI:**
```bash
# Install doctl
brew install doctl

# Authenticate
doctl auth init

# Create app from spec
doctl apps create --spec .do/app.yaml

# Set secret
doctl apps update YOUR_APP_ID --spec .do/app.yaml
```

**Via DigitalOcean Console:**
1. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Click "Create App"
3. Connect your GitHub repo: `bcharleson/nano-banana-mcp`
4. DigitalOcean will auto-detect the `.do/app.yaml` configuration
5. Add environment variable: `GEMINI_API_KEY` (mark as secret)
6. Click "Create Resources"

**One-Click Deploy:**

[![Deploy to DO](https://www.deploytodo.com/do-btn-blue.svg)](https://cloud.digitalocean.com/apps/new?repo=https://github.com/bcharleson/nano-banana-mcp/tree/main)

**Pricing:**
- Basic plan: $5/month (512MB RAM, 1 vCPU)
- Pro plan: $12/month (1GB RAM, 1 vCPU)

**Quick Deploy Script:**
```bash
# One-command deployment
./scripts/deploy-digitalocean.sh

# Test deployment
./scripts/test-deployment.sh https://your-app.ondigitalocean.app
```

### Connect to Remote Server

In `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "nano-banana-remote": {
      "url": "https://your-deployment-url.com"
    }
  }
}
```

## API Usage

### Generate Image

```python
# Via MCP tool
generate_image(
    prompt="A professional headshot of a tech entrepreneur in a modern office",
    output_path="/path/to/output.png",
    aspect_ratio="16:9",
    num_images=1
)
```

**Parameters:**
- `prompt` (str): Text description of the image to generate
- `output_path` (str, optional): File path to save the image
- `aspect_ratio` (str): One of: `1:1`, `16:9`, `9:16`, `4:3`, `3:4`
- `num_images` (int): Number of images to generate (1-4)

### Edit Image

```python
# Via MCP tool
edit_image(
    prompt="Change the background to a futuristic data center",
    reference_image_path="/path/to/input.jpg",
    output_path="/path/to/edited.png",
    aspect_ratio="16:9"
)
```

**Parameters:**
- `prompt` (str): Text description of the edit to make
- `reference_image_path` (str): Path to the reference image file
- `output_path` (str, optional): File path to save the edited image
- `aspect_ratio` (str): One of: `1:1`, `16:9`, `9:16`, `4:3`, `3:4`

## Development

### Run Locally (STDIO mode)

```bash
python server.py
```

### Run Locally (HTTP mode)

```bash
python server.py --http
```

Server runs on `http://localhost:8000` by default. Override with `PORT` environment variable:

```bash
PORT=3000 python server.py --http
```

### Test HTTP Endpoint

```bash
curl http://localhost:8000/health
```

## Nano Banana Pro Capabilities

- **Improved text rendering**: ~94% correctness across multiple languages
- **Multi-reference**: Process up to 14 reference images simultaneously
- **Identity consistency**: Maintain consistency across up to 5 human subjects
- **High resolution**: 4K output for professional use
- **Advanced reasoning**: Complex instruction following
- **Enhanced world knowledge**: Better diagrams and infographics
- **Precise control**: Lighting and camera angle control

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Your Gemini API key from Google AI Studio |
| `PORT` | No | HTTP server port (default: 8000) |

## Supported Image Formats

- **Input**: PNG, JPEG, WebP
- **Output**: PNG (base64 or file)

## API Details

The server uses the Gemini API with the key appended as a URL parameter:
```
https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent?key=YOUR_API_KEY
```

## Notes

- All generated images include SynthID watermark for provenance
- Maximum generation timeout: 120 seconds
- API rate limits apply based on your Gemini API tier

## Examples

### Generate YouTube Thumbnail

```python
generate_image(
    prompt="Professional YouTube thumbnail for a data quality video. Bold text 'QUALITY DATA 2026'. Tech entrepreneur pointing at screen. Clean modern design. 16:9 aspect ratio.",
    output_path="/Users/you/Desktop/thumbnail.png",
    aspect_ratio="16:9",
    num_images=1
)
```

### Edit Headshot Background

```python
edit_image(
    prompt="Replace the background with a modern tech office with data visualizations on screens. Keep the person in focus. Professional lighting.",
    reference_image_path="/path/to/headshot.jpg",
    output_path="/path/to/edited.png",
    aspect_ratio="1:1"
)
```

### Generate Multiple Variations

```python
generate_image(
    prompt="Minimalist logo for AI automation company. Blue and orange colors. Clean geometric shapes.",
    output_path="/path/to/logo_1.png",
    aspect_ratio="1:1",
    num_images=4  # Generates logo_1.png, logo_2.png, logo_3.png, logo_4.png
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- **GitHub**: https://github.com/bcharleson/nano-banana-mcp
- **Gemini API**: https://ai.google.dev/gemini-api/docs
- **FastMCP**: https://github.com/jlowin/fastmcp
- **MCP**: https://modelcontextprotocol.io

## Author

Brandon Charleson
- X: [@brandoncharleson](https://x.com/brandoncharleson)
- GitHub: [@bcharleson](https://github.com/bcharleson)
