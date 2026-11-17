"""
app/utils/exceptions.py
----------------------------------
Traduce los errores internos de yt-dlp a excepciones HTTP
claras y amigables para que el frontend las muestre al usuario.
"""

from fastapi import HTTPException
import yt_dlp


def handle_ytdlp_error(error: Exception) -> HTTPException:
    """
    Analiza el mensaje de error de yt-dlp o de red y retorna
    una HTTPException con el código y detalle adecuados.
    """
    error_msg = str(error).lower()

    # 1. URL no soportada o página sin videos (ej. google.com)
    if "unsupported url" in error_msg:
        return HTTPException(
            status_code=400,
            detail="El enlace ingresado no pertenece a una plataforma de video compatible."
        )

    # 2. Videos privados, eliminados o restringidos
    if any(word in error_msg for word in ["private video", "video unavailable", "removed", "not available"]):
        return HTTPException(
            status_code=404,
            detail="El video es privado, fue eliminado o no está disponible en este momento."
        )

    # 3. Bloqueos por edad o inicio de sesión requerido (común en Instagram/YouTube)
    if any(word in error_msg for word in ["sign in", "login required", "age-restricted", "cookies"]):
        return HTTPException(
            status_code=403,
            detail="Este contenido requiere iniciar sesión o tiene restricción de edad."
        )

    # 4. Errores de conexión o tiempo de espera agotado (timeout)
    if any(word in error_msg for word in ["timed out", "timeout", "connection", "network"]):
        return HTTPException(
            status_code=504,
            detail="Tiempo de espera agotado al conectar con la plataforma. Intenta de nuevo."
        )

    # 5. Cualquier otro error de extracción propio de yt-dlp
    if isinstance(error, yt_dlp.utils.DownloadError):
        return HTTPException(
            status_code=400,
            detail="No se pudo procesar el enlace. Verifica que la URL sea pública y correcta."
        )

    # 6. Error genérico no controlado del servidor
    return HTTPException(
        status_code=500,
        detail="Ocurrió un error interno inesperado al procesar el video."
    )
