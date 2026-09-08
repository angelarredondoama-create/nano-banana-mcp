#!/usr/bin/env python3
"""
Nano Banana Pro MCP Server
Google Gemini image generation via fastMCP
"""

import os
import base64
import httpx
from typing import Optional
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Nano Banana Pro")

# Add health check endpoint for cloud deployments
@mcp.resource("health://status")
def health_check() -> str:
    """Health check endpoint for load balancers and monitoring"""
    return "OK"

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME = "gemini-3-pro-image-preview"
API_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"


@mcp.tool()
async def generate_image(
    prompt: str,
    output_path: Optional[str] = None,
    aspect_ratio: str = "1:1",
    num_images: int = 1
) -> str:
    """
    Generate an image using Nano Banana Pro (Gemini 3 Pro Image).
    
    Args:
        prompt: Text description of the image to generate
        output_path: Optional file path to save the image (e.g., '/path/to/image.png')
        aspect_ratio: Image aspect ratio - options: '1:1', '16:9', '9:16', '4:3', '3:4'
        num_images: Number of images to generate (1-4)
    
    Returns:
        Status message with image location or base64 data
    """
    if not GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY environment variable not set"
    
    # Validate inputs
    valid_ratios = ["1:1", "16:9", "9:16", "4:3", "3:4"]
    if aspect_ratio not in valid_ratios:
        return f"Error: aspect_ratio must be one of {valid_ratios}"
    
    if num_images < 1 or num_images > 4:
        return "Error: num_images must be between 1 and 4"
    
    # Build request with API key in URL
    url = f"{API_ENDPOINT}?key={GEMINI_API_KEY}"
    
    # Request payload
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "responseModalities": ["image"]
            
            
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract image data from response
            if "candidates" not in result:
                return f"Error: No image generated. Response: {result}"
            
            images_data = []
            for idx, candidate in enumerate(result["candidates"]):
                if "content" in candidate and "parts" in candidate["content"]:
                    for part in candidate["content"]["parts"]:
                        if "inlineData" in part:
                            image_base64 = part["inlineData"]["data"]
                            images_data.append(image_base64)
            
            if not images_data:
                return "Error: No image data found in response"
            
            # Save or return images
            if output_path:
                # Save first image to specified path
                image_bytes = base64.b64decode(images_data[0])
                with open(output_path, "wb") as f:
                    f.write(image_bytes)
                
                # Save additional images if multiple generated
                saved_paths = [output_path]
                if len(images_data) > 1:
                    base_path = output_path.rsplit(".", 1)[0]
                    ext = output_path.rsplit(".", 1)[1] if "." in output_path else "png"
                    for idx, img_data in enumerate(images_data[1:], start=2):
                        img_path = f"{base_path}_{idx}.{ext}"
                        img_bytes = base64.b64decode(img_data)
                        with open(img_path, "wb") as f:
                            f.write(img_bytes)
                        saved_paths.append(img_path)
                
                return f"✓ Successfully generated {len(images_data)} image(s)!\nSaved to: {', '.join(saved_paths)}"
            else:
                # Return base64 data
                return f"✓ Successfully generated {len(images_data)} image(s)!\nBase64 data length: {len(images_data[0])} characters\n\nTo save images, provide an output_path parameter."
    
    except httpx.HTTPStatusError as e:
        return f"Error: API request failed with status {e.response.status_code}\n{e.response.text}"
    except Exception as e:
        return f"Error generating image: {str(e)}"


@mcp.tool()
async def edit_image(
    prompt: str,
    reference_image_path: str,
    output_path: Optional[str] = None,
    aspect_ratio: str = "1:1"
) -> str:
    """
    Edit an existing image using Nano Banana Pro.
    
    Args:
        prompt: Text description of the edit to make
        reference_image_path: Path to the reference image file
        output_path: Optional file path to save the edited image
        aspect_ratio: Image aspect ratio - options: '1:1', '16:9', '9:16', '4:3', '3:4'
    
    Returns:
        Status message with edited image location or base64 data
    """
    if not GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY environment variable not set"
    
    # Read and encode reference image
    try:
        with open(reference_image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        return f"Error reading reference image: {str(e)}"
    
    # Determine MIME type
    mime_type = "image/png"
    if reference_image_path.lower().endswith(".jpg") or reference_image_path.lower().endswith(".jpeg"):
        mime_type = "image/jpeg"
    elif reference_image_path.lower().endswith(".webp"):
        mime_type = "image/webp"
    
    # Build request with API key in URL
    url = f"{API_ENDPOINT}?key={GEMINI_API_KEY}"
    
    # Request payload with reference image
    payload = {
        "contents": [{
            "parts": [
                {
                    "text": prompt
                },
                {
                    "inlineData": {
                        "mimeType": mime_type,
                        "data": image_data
                    }
                }
            ]
        }],
        "generationConfig": {
            "responseModalities": ["image"],
            "aspectRatio": aspect_ratio,
            "numberOfImages": 1
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract edited image
            if "candidates" not in result:
                return f"Error: No image generated. Response: {result}"
            
            candidate = result["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                for part in candidate["content"]["parts"]:
                    if "inlineData" in part:
                        edited_image_base64 = part["inlineData"]["data"]
                        
                        if output_path:
                            image_bytes = base64.b64decode(edited_image_base64)
                            with open(output_path, "wb") as f:
                                f.write(image_bytes)
                            return f"✓ Successfully edited image!\nSaved to: {output_path}"
                        else:
                            return f"✓ Successfully edited image!\nBase64 data length: {len(edited_image_base64)} characters"
            
            return "Error: No image data found in response"
    
    except httpx.HTTPStatusError as e:
        return f"Error: API request failed with status {e.response.status_code}\n{e.response.text}"
    except Exception as e:
        return f"Error editing image: {str(e)}"


if __name__ == "__main__":
    import sys
    
    # Support both STDIO (local) and HTTP (remote) transports
    # Default to STDIO for Cursor integration
    # Use --http flag for remote deployment
    
    if "--http" in sys.argv:
        # HTTP/SSE mode for remote deployments
        port = int(os.getenv("PORT", "8000"))
        mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
        
    else:
        # STDIO mode for local Cursor integration
        mcp.run(transport="stdio")
