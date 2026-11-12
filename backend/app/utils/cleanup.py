"""
app/utils/cleanup.py
----------------------------------
Funciones de utilidad para la gestión, 
mantenimiento y borrado de los videos descargados.
"""

import os

def cleanup_file(path: str):
    """
    Elimina un video descargado del servidor en segundo plano 
    justo después de haber sido entregado al usuario.
    """
    try:
        if os.path.exists(path):
            os.remove(path)
            print(f"[Limpieza] Video descargado, eliminado con éxito: {path}")
    except Exception as e:
        print(f"[Error de limpieza] No se pudo borrar el video {path}: {e}")
