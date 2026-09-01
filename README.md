<<<<<<< HEAD
# Sistema de Control Integral de Confección - PATI

## Descripción del Proyecto

Sistema completo para la gestión y control del proceso de confección de la empresa PATI, desde el corte hasta la entrega final. El sistema reemplaza el proceso manual basado en hojas de cálculo y mensajes de WhatsApp, proporcionando trazabilidad completa, información en tiempo real y control robusto de la producción.

## Arquitectura del Sistema

- **Backend**: Python con FastAPI
- **Frontend**: Angular
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)

## Estructura del Proyecto

```
trabjo/
├── backend/                 # Backend Python (FastAPI)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # Punto de entrada de la aplicación
│   │   ├── models/          # Modelos de base de datos
│   │   ├── schemas/         # Esquemas Pydantic
│   │   ├── api/             # Endpoints de la API
│   │   ├── core/            # Configuración y utilidades
│   │   └── db/              # Configuración de base de datos
│   ├── requirements.txt
│   └── README.md
├── frontend/                # Frontend Angular
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/  # Componentes Angular
│   │   │   ├── services/    # Servicios HTTP
│   │   │   ├── models/      # Modelos TypeScript
│   │   │   └── app.module.ts
│   │   └── ...
│   ├── package.json
│   └── README.md
└── docs/                    # Documentación
    ├── API.md              # Documentación de la API
    ├── INSTALLATION.md     # Guía de instalación
    └── USER_GUIDE.md       # Guía de usuario
```

## Características Principales

### 1. Gestión de Corte
- Registro estructurado de datos de corte
- Generación automática de lotes trazables
- Control de referencias, colores, materiales y cantidades por talla

### 2. Gestión de Talleres
- Asignación de lotes a talleres
- Registro de remisiones
- Control de avances y entregas parciales
- Identificación de fallas en confección

### 3. Control de Producción
- Visibilidad en tiempo real del estado de producción
- Seguimiento de prendas en cada etapa (corte, en camino, en confección, listas)
- Identificación de pedidos especiales
- Medición de rendimiento de talleres

### 4. Estandarización
- Catálogos de tallas, colores, materiales y referencias
- Validación automática de datos
- Reducción de errores operativos

### 5. Reportes y Análisis
- Dashboard con métricas en tiempo real
- Reportes de rendimiento por taller
- Análisis de tiempos de entrega
- Identificación de cuellos de botella

## Instalación

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
ng serve
```

## Uso

1. Acceder a `http://localhost:4200` en el navegador
2. El backend estará disponible en `http://localhost:8000`
3. Documentación interactiva de la API en `http://localhost:8000/docs`

## Documentación Adicional

- [Guía de Instalación](docs/INSTALLATION.md)
- [Documentación de la API](docs/API.md)
- [Guía de Usuario](docs/USER_GUIDE.md)

## Tecnologías Utilizadas

### Backend
- FastAPI
- SQLAlchemy
- Pydantic
- Alembic (migraciones)

### Frontend
- Angular
- TypeScript
- RxJS
- Angular Material (UI)

## Estado del Proyecto

✅ Backend completo con FastAPI
✅ Frontend Angular con estructura base
✅ Modelos de datos completos
✅ API REST funcional
✅ Dashboard básico
🔄 Componentes frontend en desarrollo (estructura creada)

## Documentación

- [Guía de Instalación](docs/INSTALLATION.md)
- [Documentación de la API](docs/API.md)
- [Guía de Usuario](docs/USER_GUIDE.md)

## Licencia

Propietario - PATI
