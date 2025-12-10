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
from typing import Dict, Optional
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
    # Si viene "1080p" devuelve 1080, si falla devuelve 0 (mejor calidad)
    if not quality: return 0
    m = re.search(r'(\d{3,4})', quality)
    return int(m.group(1)) if m else 0

async def download_and_convert(url: str, format_ext: str = "mp4", quality: str = "720p") -> Dict:
    url = str(url)
    format_ext = (format_ext or "mp4").lower()
    
    # Validar que ffmpeg existe
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        raise HTTPException(status_code=500, detail="FFmpeg no instalado en el servidor.")

    # Configuración de altura máxima
    height = _parse_height(quality)
    
    # Lógica de formato para yt-dlp
    # "bv" = best video, "ba" = best audio.
    # Si es solo audio (mp3), descargamos 'bestaudio'.
    # Si es video, pedimos video limitado por altura + mejor audio.
    audio_only = format_ext in ["mp3", "m4a", "wav", "opus"]
    
    if audio_only:
        # Descarga mejor audio y convierte
        ydl_format = "bestaudio/best"
    else:
        # Video: bv (con altura max) + ba. 
        # El "/best" al final es un fallback por si no hay streams separados.
        if height > 0:
            ydl_format = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"
        else:
            ydl_format = "bestvideo+bestaudio/best"

    # Definimos el nombre temporal basado en el ID para evitar problemas de caracteres
    # Luego renombraremos al título final.
    temp_id = f"%(id)s_{int(datetime.datetime.utcnow().timestamp())}"
    outtmpl = os.path.join(DOWNLOAD_DIR, f"{temp_id}.%(ext)s")

    ydl_opts = {
        "outtmpl": outtmpl,
        "format": ydl_format,
        "ffmpeg_location": ffmpeg_path,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        # ESTO ES CLAVE: Fuerza a yt-dlp a unir video y audio en el contenedor deseado (mp4, mkv, etc)
        "merge_output_format": format_ext if not audio_only else None,
        "postprocessors": [],
    }

    # Si es solo audio, añadimos postprocesador para convertir a mp3/m4a
    if audio_only:
        ydl_opts["postprocessors"].append({
            'key': 'FFmpegExtractAudio',
            'preferredcodec': format_ext,
            'preferredquality': '192',
        })
    # Si es video y el formato final deseado es distinto al que baja (ej: webm -> mp4),
    # yt-dlp lo convierte automáticamente si 'merge_output_format' coincide.
    # Pero podemos forzar conversión de video si es necesario:
    elif format_ext == "mp4":
        # Asegura compatibilidad MP4
        ydl_opts["postprocessors"].append({
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        })

    # Función envoltorio para ejecutar en hilo
    def _run_yt_dlp():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Devolver info y el nombre del archivo generado
            return info, ydl.prepare_filename(info)

    try:
        info_dict, expected_filename = await asyncio.to_thread(_run_yt_dlp)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error yt-dlp: {str(e)}")

    # Recuperar el archivo real generado
    # Nota: si hubo conversión (mp3), la extensión cambió respecto a 'expected_filename' original
    base_name = os.path.splitext(expected_filename)[0]
    
    # Buscamos el archivo que realmente existe con ese ID base
    final_path = None
    possible_extensions = [format_ext, "mp4", "mkv", "webm", "mp3", "m4a"]
    
    # Buscar el archivo exacto
    for ext in possible_extensions:
        check_path = f"{base_name}.{ext}"
        if os.path.exists(check_path):
            final_path = check_path
            break
            
    if not final_path:
        # Fallback: buscar cualquier archivo que empiece con el ID
        files = [f for f in os.listdir(DOWNLOAD_DIR) if f.startswith(os.path.basename(base_name))]
        if files:
            final_path = os.path.join(DOWNLOAD_DIR, files[0])

    if not final_path or not os.path.exists(final_path):
         raise HTTPException(status_code=500, detail="Error: El archivo no se generó correctamente.")

    # Renombrar al título bonito final
    title = _safe_title(info_dict.get("title", "video"))
    clean_filename = f"{title}.{format_ext}"
    clean_path = os.path.join(DOWNLOAD_DIR, clean_filename)

    # Mover/Renombrar
    if os.path.exists(clean_path):
        os.remove(clean_path) # Sobreescribir si existe
    shutil.move(final_path, clean_path)

    # Guardar en BD (Tu lógica original)
    try:
        vm = VideoModel(
            title=title,
            filename=clean_filename,
            format=format_ext,
            quality=quality,
            platform=info_dict.get("extractor_key", "unknown"),
            download_url=f"/api/video/downloads/{clean_filename}", # OJO CON LA URL
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