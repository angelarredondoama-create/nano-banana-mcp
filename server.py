#!/usr/bin/env python3
import base64, logging, os, sys
from typing import Optional
import httpx
from fastmcp import FastMCP
from mcp.types import ImageContent
from starlette.requests import Request
from starlette.responses import PlainTextResponse
mcp=FastMCP("Nano Banana Pro")
log=logging.getLogger("nano_banana")
logging.basicConfig(level=logging.INFO,stream=sys.stderr)
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY","")
MODEL_NAME="gemini-3-pro-image-preview"
API_ENDPOINT=f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"
VALID_RATIOS=("1:1","16:9","9:16","4:3","3:4")
GEMINI_TIMEOUT_SECONDS=45.0
@mcp.resource("health://status")
def health_check()->str:return "OK"
@mcp.custom_route("/health",methods=["GET"])
async def http_health_check(request:Request)->PlainTextResponse:
    return PlainTextResponse("OK")
@mcp.tool()
def check_connection()->str:
    """Check MCP connectivity only. Does not call Gemini or spend credits."""
    return "Nano Banana MCP image-delivery-v1: OK. No Gemini request made."
async def request_image(parts,aspect_ratio,output_path):
    if not GEMINI_API_KEY:return "Error: GEMINI_API_KEY environment variable not set"
    if aspect_ratio not in VALID_RATIOS:return f"Error: aspect_ratio must be one of {VALID_RATIOS}"
    if output_path and "--http" in sys.argv:return "Error: omit output_path for remote use; the image is returned directly."
    payload={"contents":[{"parts":[{"text":f"Use an aspect ratio of {aspect_ratio}."},*parts]}],"generationConfig":{"responseModalities":["IMAGE"]}}
    try:
        log.info("Gemini request started model=%s",MODEL_NAME)
        async with httpx.AsyncClient(timeout=GEMINI_TIMEOUT_SECONDS) as client:r=await client.post(API_ENDPOINT,headers={"x-goog-api-key":GEMINI_API_KEY},json=payload)
        log.info("Gemini response status=%s",r.status_code)
        if r.status_code>=400:
            log.error("Gemini error body: %s",r.text[:1000])
            return f"Error: Gemini HTTP {r.status_code}: {r.text[:300]}"
        imgs=[]
        for c in r.json().get("candidates",[]):
            for p in (c.get("content") or {}).get("parts",[]):
                i=p.get("inlineData") or {}; mime=i.get("mimeType","image/png")
                if i.get("data") and mime.startswith("image/"):imgs.append(ImageContent(type="image",data=i["data"],mimeType=mime))
        if not imgs:return "Error: Gemini returned no image. The request may have been filtered."
        if output_path:
            with open(output_path,"wb") as f:f.write(base64.b64decode(imgs[0].data))
        log.info("Returning %s image content block(s) to MCP client",len(imgs)); return imgs
    except httpx.TimeoutException:return "Error: Gemini timed out. No automatic retry was made."
    except httpx.RequestError:return "Error: network connection to Gemini failed. No automatic retry was made."
    except Exception as e:
        log.error("Image processing failed type=%s",type(e).__name__); return "Error: image processing failed. Check the server logs for the error type."
@mcp.tool()
async def generate_image(prompt:str,output_path:Optional[str]=None,aspect_ratio:str="1:1",num_images:int=1):
    if num_images!=1:return "Error: only num_images=1 is supported; no Gemini request made."
    return await request_image([{"text":prompt}],aspect_ratio,output_path)
@mcp.tool()
async def edit_image(prompt:str,reference_image_path:Optional[str]=None,reference_image_data:Optional[str]=None,reference_image_mime:Optional[str]=None,output_path:Optional[str]=None,aspect_ratio:str="1:1"):
    if aspect_ratio not in VALID_RATIOS:return f"Error: aspect_ratio must be one of {VALID_RATIOS}"
    if not reference_image_path and not reference_image_data:return "Error: provide either reference_image_path or reference_image_data."
    if reference_image_data:
        data=reference_image_data
        mime=reference_image_mime or "image/png"
    else:
        try:
            with open(reference_image_path,"rb") as f:data=base64.b64encode(f.read()).decode("ascii")
        except OSError:return "Error: reference image is not readable on the server."
        ext=os.path.splitext(reference_image_path)[1].lower(); mime={".jpg":"image/jpeg",".jpeg":"image/jpeg",".webp":"image/webp"}.get(ext,"image/png")
    return await request_image([{"text":prompt},{"inlineData":{"mimeType":mime,"data":data}}],aspect_ratio,output_path)
if __name__=="__main__":
    if "--http" in sys.argv:mcp.run(transport="streamable-http",host="0.0.0.0",port=int(os.getenv("PORT","8000")),stateless_http=True)
    else:mcp.run(transport="stdio")
