"""
app/services/info_service.py
----------------------------------
Extrae metadatos y formatos disponibles de un enlace de video
usando yt-dlp. Devuelve una estructura normalizada para el frontend.

Función principal:
- get_video_info(url: str) -> dict

Formato de retorno (ejemplo):
{
  "title": "Título del video",
  "thumbnail": "https://...",
  "duration": 123,              # segundos
  "uploader": "Canal/autor",
  "platform": "YouTube",
  "formats": [
     { "extension": "mp4", "quality": "720p", "height": 720, "fps": 30, "vcodec": "avc1.64001F", "size": "12.4 MB", "type": "video" },
     { "extension": "mp3", "quality": "128kbps", "height": None, "fps": None, "vcodec": None, "size": "3.2 MB", "type": "audio" },
     ...
  ]
}
"""

from typing import Dict, Any, List, Optional
import asyncio
import math
import yt_dlp


# Funciones Helper 
def _bytes_to_human(n: Optional[int]) -> Optional[str]:
    """Convierte bytes a string humano (e.g. '12.4 MB')."""
    if n is None:
        return None
    if n == 0:
        return "0 B"
    sizes = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(max(n,1), 1024)))
    p = math.pow(1024, i)
    s = round(n / p, 2)
    return f"{s} {sizes[i]}"


def _normalize_format(fmt: dict) -> dict:
    """
    Normaliza un dict de formato de yt-dlp a la estructura que consume el frontend.
    Recorta datos: extension, quality (height o bitrate), height, fps, codec, estimated_size, type.
    """
    ext = fmt.get("ext")
    height = fmt.get("height")
    tbr = fmt.get("tbr")  # bitrate en kbps
    fps = fmt.get("fps")
    vcodec = fmt.get("vcodec")
    acodec = fmt.get("acodec")
    filesize = fmt.get("filesize") or fmt.get("filesize_approx")
    # Determina quality y type 
    if height:
        quality = f"{height}p"
        ftype = "video"
    elif tbr:
        quality = f"{int(tbr)}kbps"
        ftype = "audio"
    else:
        quality = fmt.get("format_note") or fmt.get("format") or "unknown"
        ftype = "audio" if (acodec and not vcodec) else "video" if (vcodec and not acodec) else "unknown"

    return {
        "extension": ext,
        "quality": quality,
        "height": height,
        "fps": fps,
        "vcodec": vcodec,
        "acodec": acodec,
        "size_bytes": filesize,
        "size": _bytes_to_human(filesize),
        "format_id": fmt.get("format_id"),
        "type": ftype,
    }


# Función principal  

async def get_video_info(url: str) -> Dict[str, Any]:
    """
    Extrae la info del video y retorna una estructura lista para el frontend.
    Ejecuta yt-dlp en un thread con asyncio.to_thread.
    """
    url = str(url)  # Importante: convertir HttpUrl -> str si es necesario

    def _extract():
        ydl_opts = {"quiet": True, "skip_download": True, "no_warnings": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return info

    info = await asyncio.to_thread(_extract)

    # Campos generales
    title = info.get("title", "")
    thumbnail = info.get("thumbnail")
    duration = info.get("duration") 
    uploader = info.get("uploader") or info.get("uploader_id") or info.get("channel")
    platform = info.get("extractor_key", "unknown")

    # Formatos de mapas: deduplicar por (ext, height, tbr) y ordenar
    raw_formats = info.get("formats", [])
    normalized: List[dict] = [_normalize_format(f) for f in raw_formats]

    # Mantener formatos únicos por (extension, quality) prefiriendo tamaño/altura mas grande
    seen = {}
    for f in normalized:
        key = (f["extension"], f["quality"])
        # conservar el que tenga más bytes o mayor altura
        prev = seen.get(key)
        if not prev:
            seen[key] = f
        else:
            # Preferiir mayor tamaño o altura
            prev_size = prev.get("size_bytes") or 0
            cur_size = f.get("size_bytes") or 0
            prev_h = prev.get("height") or 0
            cur_h = f.get("height") or 0
            if cur_size > prev_size or cur_h > prev_h:
                seen[key] = f

    formats = list(seen.values())

    # Formatos de ordenación: video by height desc, audio by bitrate desc
    def _sort_key(x):
        if x["type"] == "video":
            return (0, -(x["height"] or 0), -(x["fps"] or 0))
        if x["type"] == "audio":
            tbr = x["quality"]
            # extrae número de kbps
            try:
                num = int(''.join(filter(str.isdigit, tbr)))
            except Exception:
                num = 0
            return (1, -num)
        return (2, 0)

    formats.sort(key=_sort_key)

    return {
        "title": title,
        "thumbnail": thumbnail,
        "duration": duration,
        "uploader": uploader,
        "platform": platform,
        "formats": formats,
    }
