#!/usr/bin/env python3
"""Nano Banana MCP: return Gemini images to remote MCP clients."""

import base64
import logging
import os
import sys
from typing import Optional

import httpx
from fastmcp import FastMCP
from mcp.types import ImageContent

mcp = FastMCP("Nano Banana Pro")
log = logging.getLogger("nano_banana")
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME = "gemini-3-pro-image-preview"
API_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"
VALID_RATIOS = ("1:1", "16:9", "9:16", "4:3", "3:4")


@mcp.resource("health://status")
def health_check() -> str:
    return "OK"


@mcp.tool()
def check_connection() -> str:
    """Check MCP connectivity only. Does not call Gemini or spend credits."""
    return "Nano Banana MCP image-delivery-v1: OK. No Gemini request made."


async def request_image(parts, aspect_ratio, output_path):
    if not GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY environment variable not set"
    if aspect_ratio not in VALID_RATIOS:
        return f"Error: aspect_ratio must be one of {VALID_RATIOS}"
    # Remote clients cannot access paths on the Render filesystem.
    if output_path and "--http" in sys.argv:
        return "Error: omit output_path for remote use; the image is returned directly."
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"responseModalities": ["IMAGE"]},
    }
    # Express the requested composition without unsupported generationConfig fields.
    payload["contents"][0]["parts"] = [
        {"text": f"Use an aspect ratio of {aspect_ratio}."}, *parts
    ]
    try:
        log.info("Gemini request started model=%s", MODEL_NAME)
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                API_ENDPOINT,
                headers={"x-goog-api-key": GEMINI_API_KEY},
                json=payload,
            )
        log.info("Gemini response status=%s", response.status_code)
        if response.status_code >= 400:
            # Never echo a response body, URL, header or exception containing a key.
            return f"Error: Gemini HTTP {response.status_code}. Check model availability and project quota."
        result = response.json()
        images = []
        for candidate in result.get("candidates", []):
            for part in (candidate.get("content") or {}).get("parts", []):
                inline = part.get("inlineData") or {}
                mime = inline.get("mimeType", "image/png")
                if inline.get("data") and mime.startswith("image/"):
                    images.append(ImageContent(type="image", data=inline["data"], mimeType=mime))
        if not images:
            log.warning("Gemini returned no image")
            return "Error: Gemini returned no image. The request may have been filtered."
        if output_path:
            with open(output_path, "wb") as image_file:
                image_file.write(base64.b64decode(images[0].data))
        log.info("Returning %s image content block(s) to MCP client", len(images))
        return images
    except httpx.TimeoutException:
        log.warning("Gemini request timed out; no automatic retry")
        return "Error: Gemini timed out. No automatic retry was made."
    except httpx.RequestError:
        log.warning("Gemini network error; no automatic retry")
        return "Error: network connection to Gemini failed. No automatic retry was made."
    except Exception as exc:
        log.error("Image processing failed type=%s", type(exc).__name__)
        return "Error: image processing failed. Check the server logs for the error type."


@mcp.tool()
async def generate_image(
    prompt: str,
    output_path: Optional[str] = None,
    aspect_ratio: str = "1:1",
    num_images: int = 1,
):
    """Generate one image using Gemini (consumes API credit).

    Returns image content directly to Claude. Omit output_path for remote use.
    aspect_ratio is a composition instruction. Only num_images=1 is supported.
    """
    if num_images != 1:
        return "Error: only num_images=1 is supported; no Gemini request made."
    return await request_image([{"text": prompt}], aspect_ratio, output_path)


@mcp.tool()
async def edit_image(
    prompt: str,
    reference_image_path: str,
    output_path: Optional[str] = None,
    aspect_ratio: str = "1:1",
):
    """Edit a server-local image using Gemini (consumes API credit).

    reference_image_path must exist on the server, not on the client's computer.
    Returns image content directly. Omit output_path for remote use.
    """
    if aspect_ratio not in VALID_RATIOS:
        return f"Error: aspect_ratio must be one of {VALID_RATIOS}"
    try:
        with open(reference_image_path, "rb") as image_file:
            data = base64.b64encode(image_file.read()).decode("ascii")
    except OSError:
        return "Error: reference image is not readable on the server."
    extension = os.path.splitext(reference_image_path)[1].lower()
    mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(extension, "image/png")
    return await request_image([
        {"text": prompt}, {"inlineData": {"mimeType": mime, "data": data}}
    ], aspect_ratio, output_path)


if __name__ == "__main__":
    if "--http" in sys.argv:
        mcp.run(transport="streamable-http", host="0.0.0.0",
                port=int(os.getenv("PORT", "8000")))
    else:
        mcp.run(transport="stdio")
