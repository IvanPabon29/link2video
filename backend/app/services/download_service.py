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
from typing import Dict, Optional
from fastapi import HTTPException
from app.database.connection import db  
from app.models.video_model import VideoModel
import shutil
import re
from glob import glob
import subprocess

# Directorio de descargas
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def _safe_title(title: str) -> str:
    # Normaliza el título para filename seguro
    title = title.strip()
    # Reemplazar / \ ? % * : | " < > por _
    title = re.sub(r'[\\/:"*?<>|]+', "_", title)
    # Trim múltiples espacios
    title = re.sub(r'\s+', " ", title)
    return title or "video"


def _parse_height(quality: str) -> Optional[int]:
    # Convierte "720p","1080" -> 720,1080
    if not quality:
        return None
    m = re.search(r'(\d{3,4})', quality)
    if m:
        try:
            return int(m.group(1))
        except Exception:
            return None
    return None


def _choose_format_selector(info: dict, desired_ext: str, desired_quality: str, audio_only: bool) -> Optional[str]:
    """
    Construye un selector de formato para yt-dlp.
    - Si audio_only: devuelve None (yt-dlp usará 'bestaudio/best' y postprocessor).
    - Si desired_quality contiene un número (e.g. 720), intentamos devolver:
        'bestvideo[height<=720]+bestaudio/best[height<=720]'
      Esto cubre casos donde audio y video están en streams separados.
    - Si no hay quality pedida devolvemos None para fallback.
    """
    desired_ext = (desired_ext or "").lower()
    height = _parse_height(desired_quality)

    if audio_only:
        return None

    # Si tenemos una altura solicitada, devolvemos selector que combine bestvideo+bestaudio limitado por height
    if height:
        # Ejemplo: bestvideo[height<=720]+bestaudio/best[height<=720]
        return f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"

    # Si no se especifica height intentar preferir formatos que ya incluyen audio y video
    # Reutilizamos parte de la lógica anterior pero devolviendo el format_id directo si encontramos AV combinado.
    candidates = []
    for f in info.get("formats", []) or []:
        ext = (f.get("ext") or "").lower()
        height_f = f.get("height") or 0
        vcodec = f.get("vcodec") or ""
        acodec = f.get("acodec") or ""
        has_video = vcodec != "none" and vcodec != ""
        has_audio = acodec != "none" and acodec != ""

        # preferir formatos que contengan audio+video (para evitar archivos solo video sin audio)
        if has_video and has_audio:
            score = 0
            if ext == desired_ext and desired_ext != "":
                score += 50
            score += height_f
            candidates.append((score, f.get("format_id")))

    if not candidates:
        return None

    candidates.sort(key=lambda x: -x[0])
    return candidates[0][1]


async def download_and_convert(url: str, format: str = "mp4", quality: str = "720p") -> Dict:
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
    title = _safe_title(title_raw)

    # decidir si es audio-only (extensiones típicas)
    audio_exts = {"mp3", "m4a", "opus", "aac", "wav", "ogg"}
    audio_only = format.lower() in audio_exts

    # construir selector (puede ser None -> fallback)
    selected_format_selector = _choose_format_selector(info, format, quality, audio_only=audio_only)

    # Construir outtmpl predecible: título + extensión variable (yt-dlp determinará ext)
    # Pero para mayor predictibilidad forzamos outtmpl sin caracteres raros
    outtmpl = os.path.join(DOWNLOAD_DIR, f"{title}.%(ext)s")

    # Preparar opciones para yt-dlp
    ydl_opts = {
        "outtmpl": outtmpl,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        # evitar archivos .part persistentes si preferimos
        # "nopart": True,  # opcional: habilitar si no quieres .part
    }

    # Si pedimos audio-only, mejor usar 'bestaudio/best' y postprocessor de yt-dlp
    if audio_only:
        ydl_opts["format"] = selected_format_selector or "bestaudio/best"
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": format.lower(),
            "preferredquality": "192"
        }]
    else:
        # video+audio: si selected_format_selector es None -> usamos "bestvideo+bestaudio/best"
        ydl_opts["format"] = selected_format_selector or "bestvideo+bestaudio/best"
        # Solicitar merge a formato final (si yt-dlp puede)
        ydl_opts["merge_output_format"] = format.lower()

    # Ejecutar descarga en thread
    def _download_thread():
        # Ejecutar descarga
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Esperar y buscar el archivo final no parcial
        # Buscar archivos que comiencen por title. pero excluyendo .part
        pattern = os.path.join(DOWNLOAD_DIR, f"{title}.*")
        candidates = [p for p in glob(pattern) if not p.endswith(".part")]
        # excluir archivos temporales comunes (yt-dlp). También excluir archivos pequeños (< 2KB)
        candidates = [(p, os.path.getsize(p)) for p in candidates if os.path.isfile(p)]
        # Filtrar ficheros muy pequeños (probablemente 0 bytes o html)
        candidates = [(p, s) for (p, s) in candidates if s > 2048]  # >2KB
        if not candidates:
            # si no hay candidatos grandes, permitir menores pero informar
            candidates = [(p, os.path.getsize(p)) for p in glob(pattern) if os.path.isfile(p)]
            if not candidates:
                raise FileNotFoundError("No se generó ningún archivo tras la descarga (sin candidatos).")
        # escoger el más pesado (probablemente el final)
        candidates.sort(key=lambda x: -x[1])
        return os.path.basename(candidates[0][0])

    try:
        created_filename = await asyncio.to_thread(_download_thread)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en descarga (yt-dlp): {e}")

    created_path = os.path.join(DOWNLOAD_DIR, created_filename)

    # Ahora, if final extension matches requested -> ok
    if created_filename.lower().endswith("." + format.lower()):
        final_filename = created_filename
        final_path = created_path
    else:
        # Intentamos conversión/copy con ffmpeg
        base = os.path.splitext(created_filename)[0]
        final_filename = f"{base}.{format.lower()}"
        final_path = os.path.join(DOWNLOAD_DIR, final_filename)

        # Antes de llamar ffmpeg: comprobar que ffmpeg existe
        if shutil.which("ffmpeg") is None:
            # si no existe ffmpeg y la extensión no coincide, devolver error explicativo
            raise HTTPException(status_code=500, detail="FFmpeg no está disponible en el servidor. Es requerido para convertir/mergear formatos.")

        if audio_only:
            cmd = [
                "ffmpeg", "-y",
                "-i", created_path,
                "-vn",
                "-c:a", "copy",
                final_path
            ]
        else:
            cmd = [
                "ffmpeg", "-y",
                "-i", created_path,
                "-c:v", "copy",
                "-c:a", "copy",
                final_path
            ]

        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            # intentar re-encode si copy falla
            if not audio_only:
                cmd2 = [
                    "ffmpeg", "-y",
                    "-i", created_path,
                    "-c:v", "libx264",
                    "-preset", "fast",
                    "-c:a", "aac",
                    final_path
                ]
            else:
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
                # devolver detalle de ffmpeg para debugging
                raise HTTPException(status_code=500, detail=f"FFmpeg error: {stderr2.decode(errors='ignore')}")
        # eliminar original si se creó con otro nombre
        try:
            if os.path.exists(created_path) and created_path != final_path:
                os.remove(created_path)
        except Exception:
            pass

    # Verificar que final_path existe y tiene tamaño razonable
    if not os.path.exists(final_path) or os.path.getsize(final_path) < 1024:
        raise HTTPException(status_code=500, detail="El archivo final no existe o es demasiado pequeño tras la conversión.")

    # Guardar en DB (opcional)
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
        pass

    return {
        "filename": final_filename,
        "download_url": f"/downloads/{final_filename}",
        "message": "Descarga lista"
    }
