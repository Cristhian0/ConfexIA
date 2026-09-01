# Guía de Instalación - Sistema de Control Integral de Confección PATI

Esta guía te ayudará a instalar y configurar el sistema completo en tu entorno local.

## Requisitos Previos

### Backend (Python)
- Python 3.9 o superior
- pip (gestor de paquetes de Python)
- virtualenv (recomendado)

### Frontend (Angular)
- Node.js 18.x o superior
- npm 9.x o superior
- Angular CLI 17.x

## Instalación del Backend

### 1. Navegar al directorio del backend

```bash
cd backend
```

### 2. Crear entorno virtual (recomendado)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear un archivo `.env` en el directorio `backend/`:

```env
DATABASE_URL=sqlite:///./pati_confeccion.db
CORS_ORIGINS=http://localhost:4200,http://localhost:3000
```

### 5. Ejecutar el servidor

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en `http://localhost:8000`

La documentación interactiva de la API estará disponible en `http://localhost:8000/docs`

## Instalación del Frontend

### 1. Navegar al directorio del frontend

```bash
cd frontend
```

### 2. Instalar dependencias

```bash
npm install
```

### 3. Configurar la URL de la API

Editar `src/environments/environment.ts` si es necesario:

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1'
};
```

### 4. Ejecutar el servidor de desarrollo

```bash
ng serve
```

La aplicación estará disponible en `http://localhost:4200`

## Verificación de la Instalación

### Backend
1. Abrir `http://localhost:8000` en el navegador
2. Deberías ver un mensaje JSON con información del sistema
3. Abrir `http://localhost:8000/docs` para ver la documentación interactiva

### Frontend
1. Abrir `http://localhost:4200` en el navegador
2. Deberías ver la interfaz del sistema

## Solución de Problemas

### Error: "Module not found"
- Verificar que todas las dependencias estén instaladas
- Ejecutar `pip install -r requirements.txt` nuevamente (backend)
- Ejecutar `npm install` nuevamente (frontend)

### Error: "Port already in use"
- Cambiar el puerto del backend: `uvicorn app.main:app --reload --port 8001`
- Cambiar el puerto del frontend: `ng serve --port 4200`

### Error de CORS
- Verificar que la URL del frontend esté en `CORS_ORIGINS` en el archivo `.env`
- Reiniciar el servidor backend después de cambiar `.env`

### Base de datos no se crea
- Verificar permisos de escritura en el directorio
- Verificar la ruta en `DATABASE_URL` en el archivo `.env`

## Próximos Pasos

Una vez instalado el sistema:
1. Revisar la [Guía de Usuario](USER_GUIDE.md)
2. Consultar la [Documentación de la API](API.md)
3. Configurar los catálogos iniciales (Tallas, Colores, Materiales, Referencias)

