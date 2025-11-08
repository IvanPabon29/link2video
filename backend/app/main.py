"""
app/main.py
Punto de entrada del backend Link2Video.
Inicia FastAPI, configura CORS, eventos y registra routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.connection import connect_to_mongo, close_mongo_connection
from app.routers import video_router, jobs_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexión a MongoDB en inicio y cierre
@app.on_event("startup")
async def startup_db():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db():
    await close_mongo_connection()

# Routers reales
app.include_router(video_router.router, prefix="/api/video", tags=["Video"])
app.include_router(jobs_router.router, prefix="/api/jobs", tags=["Jobs"])

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Link2Video API en ejecución correctamente 🚀"}
