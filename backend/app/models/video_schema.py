"""
app/models/video_schema.py
-------------------------------------------------
Schemas Pydantic usados para validar datos de entrada
y salida entre frontend y backend.
-------------------------------------------------
"""

from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId



class VideoDownloadRequest(BaseModel):
    """
    Modelo de entrada (request) para procesar un video.
    """
    url: HttpUrl = Field(..., description="URL del video (YouTube, TikTok, Instagram, etc.)")
    format: Optional[str] = Field("mp4", description="Formato deseado (mp4, mp3, webm, etc.)")
    quality: Optional[str] = Field("1080p", description="Calidad de salida (144p, 480p, 720p, 1080p, etc.)")


class VideoResponse(BaseModel):
    """
    Modelo de salida (response) que representa la información
    del video ya procesado o guardado.
    """
    id: str
    title: str
    filename: str
    format: str
    quality: str
    platform: str
    download_url: str
    created_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }
        from_attributes = True
