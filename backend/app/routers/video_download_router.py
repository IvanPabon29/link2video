"""
app/routers/video_download_router.py
------------------------------------------------
Endpoint para procesar y descargar/convertir el video.

POST /api/video/download
Body: { "url": "https://...", "format": "mp4", "quality": "720p" }

Retorna:
{ "filename": "...", "download_url": "/downloads/..." }
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from app.services.download_service import download_and_convert

router = APIRouter()


class DownloadRequest(BaseModel):
    url: HttpUrl
    format: Optional[str] = Field("mp4")
    quality: Optional[str] = Field("720p")


@router.post("/download")
async def download(req: DownloadRequest):
    try:
        result = await download_and_convert(str(req.url), req.format, req.quality)
        return result
    except HTTPException:
        # re-raise HTTPException para que FastAPI lo maneje
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
