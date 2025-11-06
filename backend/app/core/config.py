"""
app/core/config.py
Configuración central del proyecto. Lee variables desde .env cuando
existe (usando python-dotenv a través de pydantic BaseSettings).
"""

from pydantic import BaseSettings, AnyUrl
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "Link2Video API"
    DEBUG: bool = True

    # MongoDB URI (ej: mongodb://user:pass@localhost:27017/link2video)
    MONGODB_URI: str = "mongodb://127.0.0.1:27017"
    MONGODB_DB: str = "link2video"

    # Carpeta base para archivos temporales (descargas / salidas)
    DOWNLOADS_DIR: str = "./app/static/downloads"

    # Orígenes permitidos en CORS (ajusta en producción)
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Tiempo (s) para mantener archivos temporales antes de borrarlos si implementas limpieza
    TEMP_FILE_TTL_SECONDS: int = 300

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
