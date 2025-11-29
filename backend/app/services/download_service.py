"""
app/services/download_service.py
-------------------------------------------
Servicio encargado de descargar y (si aplica) convertir
videos o audios desde plataformas soportadas por yt-dlp.

Principales funciones:
- download_and_convert(url, format, quality): descarga el contenido
  respetando formato y calidad solicitados, combinando video+audio
  cuando es necesario y utilizando FFmpeg para conversiones finales.

Retorna:
{
    "filename": "archivo_final.mp4",
    "download_url": "/downloads/archivo_final.mp4",
    "message": "Descarga lista"
}
"""

import os
import asyncio
import datetime
import yt_dlp
from typing import Dict, Optional
from fastapi import HTTPException
from app.database.connection import db  
from app.models.video_model import VideoModel

# Directorio de descargas
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def _choose_format(info: dict, desired_ext: str, desired_quality: str, audio_only: bool) -> Optional[str]:
    """
    Selecciona el format_id más cercano a la petición.
    - Si audio_only=True intenta priorizar tracks de audio (bestaudio).
    - Devuelve un format selector aceptado por yt-dlp (ej. "137+140" o "bestvideo+bestaudio/best" o format_id).
    """
    desired_ext = (desired_ext or "").lower()
    desired_quality = (desired_quality or "").lower()

    # Si es audio-only devolvemos None -> usar 'bestaudio/best' (yt-dlp)
    if audio_only:
        return None

    candidates = []
    for f in info.get("formats", []) or []:
        ext = (f.get("ext") or "").lower()
        height = f.get("height") or 0
        vcodec = f.get("vcodec") or ""
        acodec = f.get("acodec") or ""
        has_video = vcodec != "none" and vcodec != ""
        has_audio = acodec != "none" and acodec != ""

        # preferir formatos que contengan audio+video (para evitar archivos solo video sin audio)
        if not (has_video and has_audio):
            continue

        score = 0
        if ext == desired_ext and desired_ext != "":
            score += 50
        # calidad por altura
        if desired_quality and str(desired_quality) in f"{height}p":
            score += 30
        # preferir mayor altura
        score += height
        candidates.append((score, f.get("format_id")))

    if not candidates:
        # fallback: devolver None -> usar bestvideo+bestaudio later
        return None

    candidates.sort(key=lambda x: -x[0])
    return candidates[0][1]


async def download_and_convert(url: str, format: str = "mp4", quality: str = "720p") -> Dict:
    """
    Descarga y convierte (si aplica) un recurso multimedia.
    - url: enlace
    - format: extensión final solicitada (mp4, webm, mp3, m4a, opus, wav, etc.)
    - quality: etiqueta (720p, 1080p, 128kbps...)
    """
    url = str(url)
    format = str(format or "mp4")
    quality = str(quality or "")

    # Extraer metadata con yt-dlp en thread
    def _extract():
        ydl_opts = {"quiet": True, "no_warnings": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    info = await asyncio.to_thread(_extract)
    title_raw = info.get("title") or "video"
    title = title_raw.replace("/", "_").strip() or "video"

    # decidir si es audio-only (extensiones típicas)
    audio_exts = {"mp3", "m4a", "opus", "aac", "wav", "ogg"}
    audio_only = format.lower() in audio_exts

    # escoger format_id o fallback
    selected = _choose_format(info, format, quality, audio_only=audio_only)

    outtmpl = os.path.join(DOWNLOAD_DIR, f"{title}.%(ext)s")

    # Preparar opciones para yt-dlp
    ydl_opts = {
        "outtmpl": outtmpl,
        "quiet": True,
        "no_warnings": True,
    }

    # Si pedimos audio-only, mejor usar 'bestaudio/best' y postprocessor de yt-dlp
    if audio_only:
        ydl_opts["format"] = selected or "bestaudio/best"
        # Postprocessor para extraer audio en formato deseado (usa ffmpeg internamente)
        # preferredquality puede ser ignorado para codecs como 'm4a' pero se deja por compatibilidad
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": format.lower(),
            "preferredquality": "192"
        }]
        # Ajustar outtmpl para que yt-dlp genere <title>.<ext> por extracción
        # yt-dlp, tras postprocessor, generará el archivo final con la extensión deseada
    else:
        # video+audio: si selected es None -> usaremos bestvideo+bestaudio/best
        ydl_opts["format"] = selected or "bestvideo+bestaudio/best"
        # Solicitar mezcla a formato final (si yt-dlp puede)
        ydl_opts["merge_output_format"] = format.lower()

    # Ejecutar descarga en thread (bloqueante dentro del thread)
    def _download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Buscar archivos generados que empiecen con title
        files = [f for f in os.listdir(DOWNLOAD_DIR) if f.startswith(title + ".")]
        if not files:
            raise FileNotFoundError("No se generó ningún archivo tras la descarga.")

        # retornar el archivo más pesado (probablemente el final)
        files_with_size = [(f, os.path.getsize(os.path.join(DOWNLOAD_DIR, f))) for f in files]
        files_with_size.sort(key=lambda x: -x[1])
        return files_with_size[0][0]

    try:
        created_filename = await asyncio.to_thread(_download)
    except Exception as e:
        # incluir mensaje para debug
        raise HTTPException(status_code=500, detail=f"Error en descarga (yt-dlp): {e}")

    created_path = os.path.join(DOWNLOAD_DIR, created_filename)

    # Si el archivo ya tiene la extensión solicitada, lo usamos
    if created_filename.lower().endswith("." + format.lower()):
        final_filename = created_filename
        final_path = created_path
    else:
        # Intentamos convertir/copy streams con ffmpeg si es posible (copy streams evita re-encode)
        base = os.path.splitext(created_filename)[0]
        final_filename = f"{base}.{format.lower()}"
        final_path = os.path.join(DOWNLOAD_DIR, final_filename)

        # Si pedimos audio-only y yt-dlp no creó el formato deseado, hacer extracción con ffmpeg
        if audio_only:
            cmd = [
                "ffmpeg", "-y",
                "-i", created_path,
                "-vn",
                "-c:a", "copy",  # intentar copiar si ya tiene codec compatible
                final_path
            ]
        else:
            # video: intentar copiar streams (más rápido) y fallar a re-encode en caso necesario
            cmd = [
                "ffmpeg", "-y",
                "-i", created_path,
                "-c:v", "copy",
                "-c:a", "copy",
                final_path
            ]

        process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        _, stderr = await process.communicate()
        if process.returncode != 0:
            # si copy falla (codecs incompatibles), intentar re-encode (video -> libx264, audio -> aac/mp3)
            if not audio_only:
                # re-encode video+audio
                cmd2 = [
                    "ffmpeg", "-y",
                    "-i", created_path,
                    "-c:v", "libx264",
                    "-preset", "fast",
                    "-c:a", "aac",
                    final_path
                ]
            else:
                # re-encode audio
                codec = "libmp3lame" if format.lower() == "mp3" else "aac"
                cmd2 = [
                    "ffmpeg", "-y",
                    "-i", created_path,
                    "-vn",
                    "-c:a", codec,
                    final_path
                ]
            proc2 = await asyncio.create_subprocess_exec(*cmd2, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            _, stderr2 = await proc2.communicate()
            if proc2.returncode != 0:
                # devolver error con detalle de ffmpeg
                raise HTTPException(status_code=500, detail=f"FFmpeg error: {stderr2.decode()}")
        # eliminar el archivo original para ahorrar espacio
        try:
            if os.path.exists(created_path):
                os.remove(created_path)
        except Exception:
            pass

    # Guardar en DB (opcional, silencioso)
    try:
        vm = VideoModel(
            title=title,
            filename=final_filename,
            format=format.lower(),
            quality=quality,
            platform=info.get("extractor_key", "unknown"),
            download_url=f"/downloads/{final_filename}",
            created_at=datetime.datetime.utcnow(),
        )
        await db["videos"].insert_one(vm.model_dump(by_alias=True))
    except Exception:
        # no crítico: ignorar
        pass

    return {
        "filename": final_filename,
        "download_url": f"/downloads/{final_filename}",
        "message": "Descarga lista"
    }
