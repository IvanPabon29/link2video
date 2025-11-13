"""
app/models/video_model.py
--------------------------------
Modelo base  representa los documentos
almacenados en la colección "videos" en MongoDB.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class VideoModel(BaseModel):
    """
    Representa los metadatos de un video procesado.
    """
    id: Optional[str] = Field(alias="_id")
    title: str
    filename: str
    format: str
    quality: str
    platform: str
    download_url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
