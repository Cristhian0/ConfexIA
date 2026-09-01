# Backend - Sistema de Control Integral de Confección PATI

## Descripción

Backend desarrollado en Python con FastAPI para el sistema de control integral de confección de PATI.

## Instalación

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuración

Crear archivo `.env` basado en `.env.example`:

```env
DATABASE_URL=sqlite:///./pati_confeccion.db
CORS_ORIGINS=http://localhost:4200,http://localhost:3000
```

## Ejecución

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en `http://localhost:8000`

La documentación interactiva estará en `http://localhost:8000/docs`

## Estructura

- `app/models/` - Modelos de base de datos (SQLAlchemy)
- `app/schemas/` - Esquemas Pydantic para validación
- `app/api/` - Endpoints de la API
- `app/core/` - Configuración y utilidades
- `app/db/` - Configuración de base de datos

## Base de Datos

Por defecto se usa SQLite. Para cambiar a PostgreSQL, modificar `DATABASE_URL` en `.env`:

```env
DATABASE_URL=postgresql://usuario:password@localhost/pati_confeccion
```

