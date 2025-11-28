"""
app/services/download_service.py
-------------------------------------------
Descarga y (si aplica) convierte el video/audio usando yt-dlp + ffmpeg.

Funciones exportadas:
- download_and_convert(url: str, format: str, quality: str) -> dict

Retorna:
{ "filename": "video.mp4", "download_url": "/downloads/video.mp4", "message": "..." }
"""

import os
import asyncio
import datetime
import yt_dlp
from typing import Dict
from fastapi import HTTPException
from app.database.connection import db  
from app.models.video_model import VideoModel

# Directorio de descargas
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# Util: busca el mejor format_id según extensión/quality enviada
def _choose_format_id(info: dict, desired_ext: str, desired_quality: str) -> str | None:
    """
    Busca en info['formats'] el format_id más cercano a desired_ext+desired_quality.
    Si no encuentra coincidencia exacta, devuelve None (yt-dlp seleccionará 'best').
    """
    desired_ext = (desired_ext or "").lower()
    desired_quality = (desired_quality or "").lower()

    candidates = []
    for f in info.get("formats", []):
        ext = (f.get("ext") or "").lower()
        height = f.get("height")
        tbr = f.get("tbr")
        # text match quality: '720p' vs height
        qlabel = f"{height}p" if height else (f"{int(tbr)}kbps" if tbr else "")
        score = 0
        if ext == desired_ext:
            score += 2
        if desired_quality and qlabel and desired_quality in qlabel.lower():
            score += 3
        # prefer higher height/tbr
        score += (height or 0) + int(tbr or 0)
        candidates.append((score, f.get("format_id")))
    if not candidates:
        return None
    candidates.sort(key=lambda x: -x[0])
    return candidates[0][1]


async def download_and_convert(url: str, format: str = "mp4", quality: str = "720p") -> Dict:
    """
    Realiza la descarga y conversión si es necesario.

    - url: string (asegúrate de castearlo desde HttpUrl)
    - format: extensión solicitada (mp4, webm, mp3, m4a, opus...)
    - quality: text label (720p, 1080p, 128kbps ...)

    Retorna un diccionario con filename y download_url.
    """
    url = str(url)
    format = str(format)
    quality = str(quality)

    # 1) Extraccion de metadata (síncrono) pero en thread
    def _extract():
        opts = {"quiet": True, "no_warnings": True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    info = await asyncio.to_thread(_extract)
    title = info.get("title", "video").replace("/", "_")
    ext_orig = info.get("ext", "mp4")

    # 2) determine format id if possible
    chosen_format_id = _choose_format_id(info, format, quality)

    # 3) build yt-dlp options
    outtmpl = os.path.join(DOWNLOAD_DIR, f"{title}.%(ext)s")
    ydl_opts = {
        "format": chosen_format_id or "best",
        "outtmpl": outtmpl,
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": ext_orig,  # yt-dlp merges if video+audio
    }

    # If target is audio-only (mp3/m4a/opus) we can ask yt-dlp to extract audio directly
    audio_only = format.lower() in ("mp3", "m4a", "opus", "wav", "aac")

    if audio_only:
        # prefer bestaudio
        ydl_opts["format"] = chosen_format_id or "bestaudio/best"
        # set postprocessor to extract audio? We'll use ffmpeg conversion path for clarity
    # Execute download in thread (blocking)
    def _download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        # find generated file (yt-dlp may create <title>.<ext>)
        # choose the largest matching file with base title
        files = [f for f in os.listdir(DOWNLOAD_DIR) if f.startswith(title + ".")]
        if not files:
            raise FileNotFoundError("No se creó archivo tras descarga")
        # pick the file with largest size
        files_with_size = [(f, os.path.getsize(os.path.join(DOWNLOAD_DIR, f))) for f in files]
        files_with_size.sort(key=lambda x: -x[1])
        return files_with_size[0][0]  # filename

    try:
        created_filename = await asyncio.to_thread(_download)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"yt-dlp error: {e}")

    filepath = os.path.join(DOWNLOAD_DIR, created_filename)

    # If requested extension equals created ext -> done
    if created_filename.lower().endswith("." + format.lower()):
        final_filename = created_filename
    else:
        # Convert with ffmpeg (async)
        base = os.path.splitext(created_filename)[0]
        final_filename = f"{base}.{format}"
        final_path = os.path.join(DOWNLOAD_DIR, final_filename)

        # Build ffmpeg command
        # If audio-only requested, remove video stream (-vn) and encode audio
        if audio_only:
            cmd = [
                "ffmpeg",
                "-y",
                "-i", filepath,
                "-vn",
                "-c:a", "libmp3lame" if format == "mp3" else "aac",
                final_path
            ]
        else:
            # video conversion (re-encode with libx264 + aac)
            cmd = [
                "ffmpeg",
                "-y",
                "-i", filepath,
                "-c:v", "libx264",
                "-preset", "fast",
                "-c:a", "aac",
                final_path
            ]

        process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            # keep original file if conversion fails
            raise HTTPException(status_code=500, detail=f"FFmpeg failed: {stderr.decode()}")
        # optionally delete original file to save space
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass

    # Save metadata to DB (optional)
    try:
        video_doc = VideoModel(
            title=title,
            filename=final_filename,
            format=format,
            quality=quality,
            platform=info.get("extractor_key", "unknown"),
            download_url=f"/downloads/{final_filename}",
            created_at=datetime.datetime.utcnow(),
        )
        await db["videos"].insert_one(video_doc.model_dump(by_alias=True))
    except Exception:
        # non-fatal: log/ignore (no logging here to keep dependency-free)
        pass

    return {
        "filename": final_filename,
        "download_url": f"/downloads/{final_filename}",
        "message": "Download ready"
    }
