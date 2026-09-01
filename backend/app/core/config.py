from pydantic_settings import BaseSettings
from typing import List
import os

def _get_cors_origins() -> List[str]:
    """Obtiene los orígenes CORS según el ambiente"""
    environment = os.getenv("ENVIRONMENT", "development")
    frontend_url = os.getenv("FRONTEND_URL", "")
    
    # Orígenes por defecto para producción y desarrollo
    default_origins = [
        "http://localhost:3000",
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "http://127.0.0.1:3000",
        "https://confecciones.vercel.app",
        "https://confecciones-59k3.vercel.app",
        "https://confecciones-93r3.vercel.app",
        "https://confecciones-v2.vercel.app",
        "https://confeccionesv2.onrender.com",
        "https://pati-confeccion-frontend.vercel.app",
    ]
    
    # Agregar URL del frontend desde variable de entorno (producción)
    if frontend_url:
        default_origins.append(frontend_url)
    else:
        # Si no hay variable de entorno, agregar orígenes comunes de producción
        default_origins.extend([
            "https://confecciones.onrender.com",  # Backend en Render
        ])
    
    return default_origins

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sistema de Control Integral de Confección - PATI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Base de datos
    DATABASE_URL: str = "sqlite:///./pati_confeccion.db"
    
    # CORS - Configuración flexible para desarrollo y producción
    CORS_ORIGINS: List[str] = _get_cors_origins()
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

