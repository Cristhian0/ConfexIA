from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .db.database import engine, Base
from .api import router
from .db.migrations import ejecutar_migraciones
from .db.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password

# Crear tablas de base de datos
Base.metadata.create_all(bind=engine)

# Ejecutar migraciones para agregar nuevas columnas
try:
    ejecutar_migraciones()
except Exception as e:
    print(f"Advertencia al ejecutar migraciones: {e}")
    print("Si es la primera vez que ejecutas la aplicación, esto es normal.")

app = FastAPI(
    title="Sistema de Confección Textil",
    description="API para inventario de tela, corte, lotes, confección, calidad, inventario PT, costos y documentación",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(router, prefix="/api/v1")

# Sembrar usuarios iniciales (si no existen)
try:
    db = SessionLocal()
    existing = db.query(User).count()
    if existing == 0:
        users = [
            {"username": "Admin", "password": "admin123", "role": "admin"},
            {"username": "TallerAD", "password": "Taller123", "role": "taller"},
            {"username": "Dasbo", "password": "dasbo123", "role": "dashboard"},
        ]
        for u in users:
            user = User(username=u["username"], password_hash=hash_password(u["password"]), role=u["role"])
            db.add(user)
        db.commit()
        print("Usuarios iniciales creados: Admin, TallerAD, Dasbo")
    db.close()
except Exception as e:
    print(f"No se pudieron crear usuarios iniciales: {e}")

@app.get("/")
async def root():
    return {
        "message": "Sistema de Confección Textil",
        "version": "1.0.0",
        "docs": "/docs"
    }
@app.head("/")
async def root_head():
    return Response(status_code=200)
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

