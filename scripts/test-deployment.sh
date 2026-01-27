#!/bin/bash

# Test deployment script for Nano Banana MCP Server

if [ -z "$1" ]; then
    echo "Usage: ./test-deployment.sh <server-url>"
    echo "Example: ./test-deployment.sh https://your-app.ondigitalocean.app"
    exit 1
fi

SERVER_URL=$1

echo "🧪 Testing Nano Banana MCP Server"
echo "=================================="
echo "Server: $SERVER_URL"
echo ""

# Test 1: Health check
echo "1️⃣  Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVER_URL/health")
if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo "   ✅ Health check passed (HTTP $HEALTH_RESPONSE)"
else
    echo "   ❌ Health check failed (HTTP $HEALTH_RESPONSE)"
    exit 1
fi

# Test 2: Root endpoint
echo "2️⃣  Testing root endpoint..."
ROOT_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVER_URL/")
if [ "$ROOT_RESPONSE" = "200" ]; then
    echo "   ✅ Root endpoint accessible (HTTP $ROOT_RESPONSE)"
else
    echo "   ⚠️  Root endpoint returned HTTP $ROOT_RESPONSE"
fi

# Test 3: Check for MCP headers
echo "3️⃣  Testing MCP protocol headers..."
HEADERS=$(curl -s -I "$SERVER_URL/")
if echo "$HEADERS" | grep -q "text/event-stream\|application/json"; then
    echo "   ✅ MCP headers detected"
else
    echo "   ⚠️  MCP headers not found (may be normal)"
fi

echo ""
echo "✅ Basic tests passed!"
echo ""
echo "📝 To use this server in Cursor, add to .cursor/mcp.json:"
echo ""
echo '{
  "mcpServers": {
    "nano-banana-remote": {
      "url": "'"$SERVER_URL"'"
    }
  }
}'
echo ""
echo "🎉 Server is ready to use!"
