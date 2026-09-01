# Guía de Despliegue en Vercel

## Opción 1: Backend y Frontend en el Mismo Proyecto (Monorepo en Vercel)

### Paso 1: Crear dos aplicaciones en Vercel
1. Una para el backend (carpeta `backend/`)
2. Una para el frontend (carpeta `frontend/`)

### Paso 2: Desplegar Backend

```bash
# En Vercel Dashboard:
1. Click en "Add New" → "Project"
2. Conecta el repositorio
3. Framework: Other (Python)
4. Root Directory: backend/
5. Build Command: (dejar vacío, Vercel detecta automáticamente)
6. Output Directory: (dejar vacío)
7. Environment Variables:
   - ENVIRONMENT: production
   - FRONTEND_URL: https://your-frontend.vercel.app
```

El backend se desplegará en: `https://your-backend-app.vercel.app`

### Paso 3: Desplegar Frontend

```bash
1. Click en "Add New" → "Project"
2. Conecta el repositorio
3. Framework: Angular
4. Root Directory: frontend/
5. Build Command: npm run build
6. Output Directory: dist/pati-confeccion-frontend
7. Environment Variables:
   - API_URL: https://your-backend-app.vercel.app/api/v1
```

El frontend se desplegará en: `https://your-frontend.vercel.app`

### Paso 4: Configurar CORS en el Backend

En Vercel Dashboard del backend:
- Ir a Settings → Environment Variables
- Agregar/actualizar: `FRONTEND_URL=https://your-frontend.vercel.app`

---

## Opción 2: Backend en Vercel + Frontend en Vercel con Proxy

### Ventaja: El frontend puede usar URLs relativas `/api/v1`

1. Desplegar backend como se describe arriba
2. En `frontend/vercel.json`, actualizar:
```json
"rewrites": [
  {
    "source": "/api/:path*",
    "destination": "https://your-backend-app.vercel.app/api/:path*"
  }
]
```

3. Mantener en `environment.prod.ts`: `apiUrl: '/api/v1'`

---

## Opción 3: Backend en Railway/Heroku + Frontend en Vercel

Si prefieres usar otro servicio para el backend:

### Railway
```bash
1. Conecta el repositorio
2. Variables de entorno:
   - ENVIRONMENT: production
   - FRONTEND_URL: https://your-frontend.vercel.app
   - PORT: Railway asigna automáticamente
```

Backend en: `https://your-railway-app.railway.app`

### Configurar Frontend
- En `environment.prod.ts` o `.env.production`:
```
API_URL=https://your-railway-app.railway.app/api/v1
```

---

## Checklist Final

- [ ] Backend desplegado en Vercel/Railway
- [ ] Frontend desplegado en Vercel
- [ ] CORS configurado correctamente (FRONTEND_URL en backend)
- [ ] API_URL en frontend apunta al backend correcto
- [ ] Environment.prod.ts tiene la URL correcta
- [ ] Test: Acceder a frontend → verificar que las APIs funcionan
- [ ] Test: Verificar en DevTools que las requests van al backend correcto

## Comandos Locales para Probar

```bash
# Terminal 1: Backend
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python run_server.py

# Terminal 2: Frontend
cd frontend
npm install
ng serve

# Acceder a http://localhost:4200
# Las APIs irán a http://localhost:8001/api/v1
```

## Solución de Problemas

### Error CORS
- Verificar FRONTEND_URL en backend está correcto
- Verificar que el backend tiene el frontend URL en CORS_ORIGINS

### Frontend no conecta con backend
- Verificar API_URL en environment.prod.ts
- Verificar que no hay typos en la URL
- Verificar en DevTools → Network que la request va a la URL correcta

### Base de datos en Vercel
- Actualmente usa SQLite (archivo local)
- Para producción, considera migrar a PostgreSQL/MySQL
- Variables: DATABASE_URL=postgresql://user:pass@host/db

