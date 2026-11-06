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

# Directorio de descargas
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def _safe_title(title: str) -> str:
    # Limpieza básica del título
    title = re.sub(r'[\\/:"*?<>|]+', "_", title)
    return title.strip() or "video"

def _parse_height(quality: str) -> int:
    if not quality: return 0
    m = re.search(r'(\d{3,4})', quality)
    return int(m.group(1)) if m else 0

async def download_and_convert(url: str, format_ext: str = "mp4", quality: str = "720p") -> Dict:
    url = str(url)
    format_ext = (format_ext or "mp4").lower()
    
    # Verificar FFmpeg
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        local_ffmpeg = os.path.join(os.getcwd(), "ffmpeg.exe")
        if os.path.exists(local_ffmpeg):
            ffmpeg_path = local_ffmpeg
        else:
            raise HTTPException(status_code=500, detail="FFmpeg no encontrado.")

    # Generar ID
    timestamp = int(datetime.datetime.utcnow().timestamp())
    filename_base = f"temp_{timestamp}" 
    outtmpl = os.path.join(DOWNLOAD_DIR, f"{filename_base}.%(ext)s")

    audio_only = format_ext in ["mp3", "m4a", "wav", "opus"]
    height = _parse_height(quality)

    # Opciones Base con límite de tiempo para evitar congelamientos (timeouts)
    ydl_opts = {
        "outtmpl": outtmpl,
        "ffmpeg_location": ffmpeg_path,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "overwrites": True,
        "socket_timeout": 30,  # Evita que se quede colgado indefinidamente
    }

    if audio_only:
        # SOLUCIÓN AUDIO ESTRICTA (MP3/M4A)
        # Formato: Solo el mejor audio disponible.
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": format_ext,  # mp3, m4a, wav
                "preferredquality": "192",
            }],
            "post_process_ext": format_ext 
        })
    else:
        # === ESTRATEGIA VIDEO CON AUDIO OPTIMIZADA ===
        # Selecciona el mejor video hasta la altura deseada y lo combina con el mejor audio
        if height > 0:
            ydl_format = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"
        else:
            ydl_format = "bestvideo+bestaudio/best"

        ydl_opts.update({
            "format": ydl_format,
            "merge_output_format": format_ext,  # Fusión nativa y limpia mediante FFmpeg sin recodificaciones forzadas
        })

    def _run_yt_dlp():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return info

    try:
        info_dict = await asyncio.to_thread(_run_yt_dlp)
    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Error descarga: {str(e)}")

    # === BÚSQUEDA DEL ARCHIVO FINAL ===
    expected_file = f"{filename_base}.{format_ext}"
    final_path_temp = os.path.join(DOWNLOAD_DIR, expected_file)

    # Búsqueda de seguridad por si FFmpeg cambió la extensión o ajustó el contenedor
    if not os.path.exists(final_path_temp):
        found = False
        for f in os.listdir(DOWNLOAD_DIR):
            if f.startswith(filename_base) and f.endswith(f".{format_ext}"):
                final_path_temp = os.path.join(DOWNLOAD_DIR, f)
                found = True
                break
        if not found:
            raise HTTPException(status_code=500, detail="Error: El archivo no se generó correctamente.")

    # Renombrar y Mover al nombre final limpio con el título del video
    title = _safe_title(info_dict.get("title", "video"))
    clean_filename = f"{title}.{format_ext}"
    clean_path = os.path.join(DOWNLOAD_DIR, clean_filename)

    if os.path.exists(clean_path):
        os.remove(clean_path)
    shutil.move(final_path_temp, clean_path)

    # Limpieza de basura (archivos temporales independientes antes del merge)
    for f in os.listdir(DOWNLOAD_DIR):
        if f.startswith(filename_base):
            try:
                os.remove(os.path.join(DOWNLOAD_DIR, f))
            except:
                pass

    # Registro en Base de Datos (Opcional, protegido contra fallos de DB)
    try:
        vm = VideoModel(
            title=title,
            filename=clean_filename,
            format=format_ext,
            quality=quality,
            platform=info_dict.get("extractor_key", "unknown"),
            download_url=f"/api/video/downloads/{clean_filename}",
            created_at=datetime.datetime.utcnow(),
        )
        await db["videos"].insert_one(vm.model_dump(by_alias=True))
    except Exception:
        pass

    return {
        "filename": clean_filename,
        "download_url": f"/api/video/downloads/{clean_filename}",
        "status": "success"
    }
