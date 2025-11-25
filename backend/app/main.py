"""
app/main.py
----------------------------------
Punto de entrada del backend Link2Video.
Inicia FastAPI, configura CORS, eventos y registra routers.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Importaciones locales
from app.core.config import settings
from app.database.connection import connect_to_mongo, close_mongo_connection
from app.routers import video_info_router, video_download_router 

#  Inicialización de la app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
)

#  Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  Montar archivos estáticos
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

#  Eventos de conexión MongoDB
@app.on_event("startup")
async def startup_db():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db():
    await close_mongo_connection()

#  Registro de routers
app.include_router(video_info_router.router, prefix="/api/video", tags=["Video"])
app.include_router(video_download_router.router, prefix="/api/video", tags=["Video"])
# app.include_router(jobs_router.router, prefix="/api/jobs", tags=["Jobs"])

#  Endpoint raíz
@app.get("/", tags=["Root"])
async def root():
    return {"message": "✅ Link2Video API en ejecución correctamente !"}
