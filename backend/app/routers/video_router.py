"""
app/routers/video_router.py
--------------------------------
Router principal para procesar, listar y eliminar videos.

Endpoints:
- POST /api/video/download  → procesa un enlace y descarga/convierte el video
- GET  /api/video/list      → obtiene lista de videos procesados guardados en MongoDB
- DELETE /api/video/delete/{id} → elimina un video de la base de datos y su archivo

Depende de:
- app/services/video_service.py  → lógica de descarga/convertir (yt-dlp + ffmpeg)
- app/database/connection.py     → conexión MongoDB
- app/models/video_schema.py      → esquemas Pydantic para validar requests/responses
--------------------------------
"""

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
from bson import ObjectId
from app.services.video_service import process_video, list_videos_db, delete_video_db
from app.models.video_schema import VideoDownloadRequest, VideoResponse

router = APIRouter()


@router.post("/download", status_code=202)
async def download_video(request: VideoDownloadRequest, background_tasks: BackgroundTasks):
    """
    Procesa un enlace de video y devuelve su información.
    El procesamiento (descarga/conversión) se ejecuta en segundo plano.

    Args:
        request: Datos enviados por el cliente (url, formato, calidad)
        background_tasks: Cola interna para ejecutar tareas asíncronas

    Returns:
        JSON con información inicial del video o error.
    """
    try:
        background_tasks.add_task(process_video, request.url, request.format, request.quality)
        return {
            "message": "Procesamiento iniciado",
            "url": str(request.url)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el video: {str(e)}")


@router.get("/list", response_model=list[VideoResponse])
async def list_videos():
    """Devuelve la lista de videos procesados guardados en MongoDB."""
    try:
        videos = await list_videos_db()
        return videos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudieron listar los videos: {str(e)}")


@router.delete("/delete/{video_id}")
async def delete_video(video_id: str):
    """Elimina un video tanto de MongoDB como del almacenamiento local."""
    try:
        if not ObjectId.is_valid(video_id):
            raise HTTPException(status_code=400, detail="ID inválido")

        deleted = await delete_video_db(video_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Video no encontrado")

        return {"message": "Video eliminado correctamente", "id": video_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar el video: {str(e)}")
