"""
app/routers/video_download_router.py
------------------------------------------------
Endpoint para procesar/convertir  y descargar el video.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from app.services.download_service import download_and_convert
from fastapi.responses import FileResponse
import os

router = APIRouter()

# Reinsertar la definición del directorio de descargas
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads") 
# Asegurarse de que DOWNLOAD_DIR exista (aunque ya está en el servicio)
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Reinsertar el esquema Pydantic 
class DownloadRequest(BaseModel):
    url: HttpUrl
    format: Optional[str] = Field("mp4", description="Formato de salida (mp4, mp3, webm, m4a, etc.)")
    quality: Optional[str] = Field("1080p", description="Calidad deseada (720p, 1080p, 4k, etc.)")

# Endpoint para iniciar la descarga y conversión del video
@router.post("/download")
async def download(req: DownloadRequest):
    try:
        # 1. Procesamos el video (usando el servicio actualizado)
        result = await download_and_convert(str(req.url), req.format, req.quality)
        
        # 2. Obtenemos la ruta real del archivo generado
        filename = result["filename"]
        file_path = os.path.join(DOWNLOAD_DIR, filename)
        
        # Validación de seguridad: Asegurar que el archivo exista
        if not os.path.exists(file_path):
             raise HTTPException(status_code=500, detail="Error de servidor: Archivo no encontrado después de la descarga.")
        
        # 3. Devolvemos el ARCHIVO directamente
        return FileResponse(
            file_path, 
            filename=filename, 
            media_type="application/octet-stream" # Tipo binario para descarga
        )
        
    except HTTPException:
        # Re-lanzar HTTPException para que FastAPI lo maneje con el código correcto
        raise
    except Exception as e:
        # Capturar otros errores no controlados y devolver 500
        raise HTTPException(status_code=500, detail=str(e))