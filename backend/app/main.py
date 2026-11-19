"""
app/main.py
----------------------------------
Punto de entrada del backend Link2Video.
Inicia FastAPI, configura CORS, gestiona el ciclo de vida (lifespan) y registra routers.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Importaciones locales
from app.core.config import settings
from app.database.connection import connect_to_mongo, close_mongo_connection
from app.routers import video_info_router, video_download_router 


# Gestión moderna del ciclo de vida (reemplaza a @app.on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Inicio de la aplicación (Startup) ---
    os.makedirs("downloads", exist_ok=True)
    await connect_to_mongo()
    yield
    # --- Apagado de la aplicación (Shutdown) ---
    await close_mongo_connection()


# Inicialización de la app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Configuración de CORS (incluye expose_headers para leer Content-Disposition en el frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# Asegurar directorio antes de montar archivos estáticos
os.makedirs("downloads", exist_ok=True)
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

# Registro de routers
app.include_router(video_info_router.router, prefix="/api/video", tags=["Video"])
app.include_router(video_download_router.router, prefix="/api/video", tags=["Video"])

# Endpoint raíz
@app.get("/", tags=["Root"])
async def root():
    return {"message": "✅ Link2Video API en ejecución correctamente"}
