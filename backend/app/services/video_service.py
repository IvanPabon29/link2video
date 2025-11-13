"""
app/services/video_service.py
---------------------------------
Servicio central que maneja la lógica real de descarga, conversión
y gestión de videos mediante yt-dlp y FFmpeg.

Funciones principales:
- process_video(url, format, quality): descarga y convierte el video.
- list_videos_db(): obtiene los registros guardados.
- delete_video_db(video_id): elimina el video del sistema y la base de datos.
"""

import os
import asyncio
import datetime
import yt_dlp
import subprocess
from bson import ObjectId
from fastapi import HTTPException
from app.database.connection import db
from app.core.config import settings
from app.models.video_model import VideoModel


#  CONFIGURACIÓN GENERAL

DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


#  FUNCIÓN PRINCIPAL

async def process_video(url: str, format: str = "mp4", quality: str = "720p"):
    """
    Descarga y convierte un video desde YouTube, TikTok, etc.
    usando yt-dlp y ffmpeg.

    Args:
        url (str): Enlace del video.
        format (str): Formato de salida (mp4, mp3, webm, etc.).
        quality (str): Resolución deseada (480p, 720p, 1080p, etc.).

    Raises:
        HTTPException: si ocurre un error durante la descarga o conversión.
    """

    try:
        # === Extraer metadatos del video ===
        ydl_opts_info = {"quiet": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title", "video_sin_titulo").replace("/", "_")
            ext = info.get("ext", "mp4")
            platform = info.get("extractor_key", "desconocida")

        filename = f"{title}.{ext}"
        filepath = os.path.join(DOWNLOAD_DIR, filename)

        # === Configurar opciones de descarga ===
        ydl_opts = {
            "format": "bestvideo[height<=1080]+bestaudio/best",
            "outtmpl": filepath,
            "quiet": True,
            "merge_output_format": ext
        }

        # === Descargar el video con yt-dlp ===
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # === Si el formato solicitado no coincide, convertir con ffmpeg ===
        if format and not filename.endswith(format):
            converted_filename = f"{title}.{format}"
            converted_filepath = os.path.join(DOWNLOAD_DIR, converted_filename)

            command = [
                "ffmpeg",
                "-i", filepath,
                "-vn" if format == "mp3" else "-c:v", "libx264",
                "-c:a", "aac",
                "-strict", "experimental",
                converted_filepath,
                "-y"
            ]

            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                raise Exception(f"Error en FFmpeg: {stderr.decode()}")

            # Eliminar el archivo original si se creó la conversión
            if os.path.exists(filepath):
                os.remove(filepath)

            filepath = converted_filepath
            filename = converted_filename

        # === Guardar metadatos en MongoDB ===
        video_doc = VideoModel(
            title=title,
            filename=filename,
            format=format,
            quality=quality,
            platform=platform,
            download_url=f"/downloads/{filename}",
            created_at=datetime.datetime.utcnow(),
        )

        await db["videos"].insert_one(video_doc.model_dump(by_alias=True))
        print(f" Video procesado y guardado: {filename}")
        return {"message": "Video procesado correctamente", "filename": filename}

    except Exception as e:
        print(f" Error procesando video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


#  LISTAR VIDEOS GUARDADOS

async def list_videos_db():
    """
    Devuelve una lista de todos los videos registrados en MongoDB.
    """
    videos_cursor = db["videos"].find().sort("created_at", -1)
    videos = []
    async for video in videos_cursor:
        video["_id"] = str(video["_id"])
        videos.append(video)
    return videos


#  ELIMINAR VIDEO

async def delete_video_db(video_id: str):
    """
    Elimina un video de la base de datos y su archivo del disco.
    """
    video = await db["videos"].find_one({"_id": ObjectId(video_id)})
    if not video:
        return False

    filepath = os.path.join(DOWNLOAD_DIR, video["filename"])
    if os.path.exists(filepath):
        os.remove(filepath)

    await db["videos"].delete_one({"_id": ObjectId(video_id)})
    return True
