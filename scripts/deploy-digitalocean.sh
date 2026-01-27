#!/bin/bash
set -e

echo "🚀 Nano Banana MCP - DigitalOcean Deployment"
echo "============================================"
echo ""

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo "❌ doctl CLI not found. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install doctl
    else
        echo "Please install doctl manually: https://docs.digitalocean.com/reference/doctl/how-to/install/"
        exit 1
    fi
fi

# Check if authenticated
echo "🔐 Checking DigitalOcean authentication..."
if ! doctl auth list &> /dev/null; then
    echo "Please authenticate with DigitalOcean:"
    doctl auth init
fi

# Check for API key
if [ -z "$GEMINI_API_KEY" ]; then
    echo ""
    echo "⚠️  GEMINI_API_KEY not found in environment"
    echo "Please enter your Gemini API key:"
    read -s GEMINI_API_KEY
    echo ""
fi

# Check if app already exists
APP_NAME="nano-banana-mcp"
echo "📦 Checking for existing app..."
APP_ID=$(doctl apps list --format ID,Spec.Name --no-header | grep "$APP_NAME" | awk '{print $1}' || echo "")

if [ -n "$APP_ID" ]; then
    echo "✅ Found existing app: $APP_ID"
    echo "🔄 Updating app..."
    
    # Update the app
    doctl apps update "$APP_ID" --spec .do/app.yaml
    
    # Update secrets
    echo "🔑 Updating secrets..."
    doctl apps update "$APP_ID" --env "GEMINI_API_KEY=$GEMINI_API_KEY"
    
else
    echo "🆕 Creating new app..."
    
    # Create the app
    APP_ID=$(doctl apps create --spec .do/app.yaml --format ID --no-header)
    
    echo "✅ App created: $APP_ID"
    
    # Set secrets
    echo "🔑 Setting secrets..."
    sleep 5  # Wait for app to be ready
    doctl apps update "$APP_ID" --env "GEMINI_API_KEY=$GEMINI_API_KEY"
fi

echo ""
echo "⏳ Waiting for deployment to complete..."
sleep 10

# Get app details
APP_URL=$(doctl apps get "$APP_ID" --format DefaultIngress --no-header)

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 App Details:"
echo "   App ID: $APP_ID"
echo "   URL: https://$APP_URL"
echo ""
echo "🔍 Useful commands:"
echo "   View logs:   doctl apps logs $APP_ID --follow"
echo "   Get status:  doctl apps get $APP_ID"
echo "   List apps:   doctl apps list"
echo ""
echo "🎉 Your MCP server is now live!"
echo ""
echo "📝 Add to .cursor/mcp.json:"
echo '{
  "mcpServers": {
    "nano-banana-remote": {
      "url": "https://'"$APP_URL"'"
    }
  }
}'
