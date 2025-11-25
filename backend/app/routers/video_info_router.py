"""
app/routers/video_info_router.py
-------------------------------------
Endpoint para obtener metadata y lista de formatos disponibles.

POST /api/video/info
Body: { "url": "https://..." }
Response: JSON con campos title, thumbnail, duration, uploader, platform, formats[]
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from app.services.info_service import get_video_info

router = APIRouter()

 
class InfoRequest(BaseModel):
    url: HttpUrl

@router.post("/info")
async def video_info(req: InfoRequest):
    try:
        info = await get_video_info(str(req.url))
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
