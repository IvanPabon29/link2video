"""
app/core/config.py
Configuración central del backend Link2Video.
Carga las variables de entorno y expone la configuración global.
"""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Link2Video API"
    DEBUG: bool = True
    VERSION: str = "1.0.0"

    # Configuración de MongoDB
    MONGODB_URL: str
    MONGODB_DB_NAME: str

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]

    class Config:
        env_file = ".env"

# Instancia global de configuración
settings = Settings()
