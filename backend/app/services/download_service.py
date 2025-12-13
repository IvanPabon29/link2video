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

    # Generar ID temporal único
    timestamp = int(datetime.datetime.utcnow().timestamp())
    filename_base = f"temp_{timestamp}" 
    # Usamos %(ext)s porque no sabemos qué bajará primero yt-dlp
    outtmpl = os.path.join(DOWNLOAD_DIR, f"{filename_base}.%(ext)s")

    audio_only = format_ext in ["mp3", "m4a", "wav", "opus"]
    height = _parse_height(quality)

    # === CONFIGURACIÓN BASE ===
    ydl_opts = {
        "outtmpl": outtmpl,
        "ffmpeg_location": ffmpeg_path,
        "quiet": True, 
        "no_warnings": True,
        "noplaylist": True,
        "overwrites": True,
    }

    if audio_only:
        # === SOLUCIÓN AUDIO (M4A/MP3) ===
        # Forzamos "bestaudio" para que NO baje fragmentos de video.
        ydl_opts.update({
            "format": "bestaudio/best", 
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": format_ext, # mp3, m4a
                "preferredquality": "192",
            }],
        })
    else:
        # === SOLUCIÓN VIDEO (MP4) ===
        # El problema del audio mudo es codec Opus en MP4.
        # ESTRATEGIA: 
        # 1. Bajar Video+Audio en su formato nativo (suele ser webm o mkv).
        # 2. Usar FFmpegVideoConvertor para pasarlo a MP4 estandar (H264 + AAC).
        
        if height > 0:
            ydl_format = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"
        else:
            ydl_format = "bestvideo+bestaudio/best"

        ydl_opts.update({
            "format": ydl_format,
            # Paso 1: Que lo una en MKV (que acepta cualquier codec sin fallar)
            "merge_output_format": "mkv", 
            "postprocessors": [{
                # Paso 2: Convertir ese MKV a MP4 real compatible con Windows
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }],
        })

    # Ejecución
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
    # El archivo final tendrá el nombre base + la extensión solicitada
    # (porque el postprocesador ya lo convirtió)
    expected_file = f"{filename_base}.{format_ext}"
    final_path_temp = os.path.join(DOWNLOAD_DIR, expected_file)

    # Si no está, es posible que FFmpegVideoConvertor no haya cambiado la extensión 
    # o haya ocurrido algo raro. Buscamos fallback seguro por nombre base.
    if not os.path.exists(final_path_temp):
        found = False
        for f in os.listdir(DOWNLOAD_DIR):
            if f.startswith(filename_base) and f.endswith(f".{format_ext}"):
                final_path_temp = os.path.join(DOWNLOAD_DIR, f)
                found = True
                break
        if not found:
             # Debug: listar carpeta
            print(f"ARCHIVOS EN DIR: {os.listdir(DOWNLOAD_DIR)}")
            raise HTTPException(status_code=500, detail="Error: El archivo no se generó correctamente.")

    # Renombrar y Mover
    title = _safe_title(info_dict.get("title", "video"))
    clean_filename = f"{title}.{format_ext}"
    clean_path = os.path.join(DOWNLOAD_DIR, clean_filename)

    if os.path.exists(clean_path):
        os.remove(clean_path)
    shutil.move(final_path_temp, clean_path)

    # Limpieza de archivos temporales sobrantes (importante si M4A bajó video extra)
    for f in os.listdir(DOWNLOAD_DIR):
        if f.startswith(filename_base):
            try:
                os.remove(os.path.join(DOWNLOAD_DIR, f))
            except:
                pass

    # DB
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