"""
app/core/database.py
Conexión asíncrona a MongoDB usando motor.motor_asyncio.
Provee helpers para obtener la db y la colección de 'downloads'.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from .config import settings

_client: Optional[AsyncIOMotorClient] = None
_db = None


def get_client() -> AsyncIOMotorClient:
    """
    Inicializa y devuelve el cliente de MongoDB (singleton).
    Llamar desde código que se ejecute en startup o cuando sea necesario.
    """
    global _client, _db
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGODB_URI)
        _db = _client[settings.MONGODB_DB]
    return _client


def get_db():
    """
    Devuelve la instancia de la base de datos (motor).
    """
    get_client()
    return _db


def get_downloads_collection():
    """
    Convenience: devuelve la colección 'downloads'.
    """
    db = get_db()
    return db["downloads"]
