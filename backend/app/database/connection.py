"""
app/database/connection.py
Módulo para manejar la conexión con MongoDB usando motor.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

# Cliente global de MongoDB
client: AsyncIOMotorClient = None
db = None

async def connect_to_mongo():
    """Establece la conexión con MongoDB al iniciar la app."""
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    print("✅ Conectado correctamente a MongoDB")

async def close_mongo_connection():
    """Cierra la conexión con MongoDB al apagar la app."""
    global client
    if client:
        client.close()
        print("🧩 Conexión con MongoDB cerrada")
