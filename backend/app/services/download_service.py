"""
app/services/download_service.py
-------------------------------------------
Servicio encargado de descargar y (si aplica) convertir
videos o audios desde plataformas soportadas por yt-dlp.

Principales funciones:
- download_and_convert(url, format, quality): descarga el contenido
  respetando formato y calidad solicitados, combinando video+audio
  cuando es necesario y utilizando FFmpeg para conversiones finales.
"""
import os
import asyncio
import datetime
import yt_dlp
import shutil
import re
from typing import Dict
from fastapi import HTTPException
from app.database.connection import db  
from app.models.video_model import VideoModel
from app.utils.exceptions import handle_ytdlp_error

# Directorio de descargas
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def _safe_title(title: str) -> str:
    """Limpieza básica del título para evitar caracteres inválidos en sistemas de archivos."""
    title = re.sub(r'[\\/:"*?<>|]+', "_", title)
    return title.strip()[:100] or "video"  # Limitamos a 100 caracteres para evitar errores de ruta larga en Windows


def _parse_height(quality: str) -> int:
    if not quality:
        return 0
    m = re.search(r'(\d{3,4})', quality)
    return int(m.group(1)) if m else 0


def _cleanup_temp_prefix(prefix: str):
    """Elimina cualquier archivo temporal o parcial (.part, .ytdl) asociado a una descarga fallida o completada."""
    for f in os.listdir(DOWNLOAD_DIR):
        if f.startswith(prefix):
            try:
                os.remove(os.path.join(DOWNLOAD_DIR, f))
            except Exception:
                pass


async def download_and_convert(url: str, format_ext: str = "mp4", quality: str = "720p") -> Dict:
    url = str(url).strip()
    format_ext = (format_ext or "mp4").lower()
    
    # Verificar FFmpeg (soporta entorno global Linux y local Windows)
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        local_ffmpeg = os.path.join(os.getcwd(), "ffmpeg.exe")
        if os.path.exists(local_ffmpeg):
            ffmpeg_path = local_ffmpeg
        else:
            raise HTTPException(status_code=500, detail="FFmpeg no encontrado en el servidor.")

    # Generar ID único para archivos temporales
    timestamp = int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000)
    filename_base = f"temp_{timestamp}" 
    outtmpl = os.path.join(DOWNLOAD_DIR, f"{filename_base}.%(ext)s")

    audio_only = format_ext in ["mp3", "m4a", "wav", "opus"]
    height = _parse_height(quality)

    # Opciones Base con límite de tiempo para evitar congelamientos
    ydl_opts = {
        "outtmpl": outtmpl,
        "ffmpeg_location": ffmpeg_path,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "overwrites": True,
        "socket_timeout": 30,
    }

    if audio_only:
        # SOLUCIÓN AUDIO ESTRICTA (MP3/M4A)
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": format_ext,
                "preferredquality": "192",
            }],
            "post_process_ext": format_ext 
        })
    else:
        # === ESTRATEGIA VIDEO UNIVERSAL (Compatible con YouTube, Instagram, TikTok, etc.) ===
        if height > 0:
            ydl_format = f"best[height<={height}]/bestvideo[height<={height}]+bestaudio/best"
        else:
            ydl_format = "best/bestvideo+bestaudio"

        ydl_opts.update({
            "format": ydl_format,
            "merge_output_format": format_ext,
        })

    def _run_yt_dlp():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=True)

    try:
        info_dict = await asyncio.to_thread(_run_yt_dlp)
    except Exception as e:
        _cleanup_temp_prefix(filename_base)
        print(f"ERROR EN DESCARGA: {e}")
        raise handle_ytdlp_error(e)

    if not info_dict:
        _cleanup_temp_prefix(filename_base)
        raise HTTPException(status_code=404, detail="No se pudo obtener el contenido del enlace.")

    # === BÚSQUEDA DEL ARCHIVO FINAL ===
    expected_file = f"{filename_base}.{format_ext}"
    final_path_temp = os.path.join(DOWNLOAD_DIR, expected_file)

    if not os.path.exists(final_path_temp):
        found = False
        for f in os.listdir(DOWNLOAD_DIR):
            if f.startswith(filename_base) and f.endswith(f".{format_ext}"):
                final_path_temp = os.path.join(DOWNLOAD_DIR, f)
                found = True
                break
        if not found:
            _cleanup_temp_prefix(filename_base)
            raise HTTPException(status_code=500, detail="Error: El archivo no se generó correctamente tras la conversión.")

    # Renombrar y Mover al nombre final limpio con el título del video
    title = _safe_title(info_dict.get("title", "video"))
    clean_filename = f"{title}.{format_ext}"
    clean_path = os.path.join(DOWNLOAD_DIR, clean_filename)

    if os.path.exists(clean_path):
        os.remove(clean_path)
    shutil.move(final_path_temp, clean_path)

    # Limpieza de residuos temporales independientes
    _cleanup_temp_prefix(filename_base)

    # Registro en Base de Datos (Opcional, protegido contra fallos de DB)
    try:
        vm = VideoModel(
            title=title,
            filename=clean_filename,
            format=format_ext,
            quality=quality,
            platform=info_dict.get("extractor_key", "unknown"),
            download_url=f"/api/video/downloads/{clean_filename}",
            created_at=datetime.datetime.now(datetime.timezone.utc),
        )
        await db["videos"].insert_one(vm.model_dump(by_alias=True))
    except Exception:
        pass

    return {
        "filename": clean_filename,
        "download_url": f"/api/video/downloads/{clean_filename}",
        "status": "success"
    }
