# 🚀 DESPLIEGUE RÁPIDO EN VERCEL - PASOS INMEDIATOS

## ✅ Lo que ya está configurado:

1. **Backend adaptado para Vercel**
   - ✅ Lee puerto y host de variables de entorno
   - ✅ CORS configurable para cualquier dominio
   - ✅ `vercel.json` listo para desplegar

2. **Frontend preparado**
   - ✅ `vercel.json` con rewrite de API
   - ✅ `environment.prod.ts` acepta URL del backend
   - ✅ Scripts de build correctos

---

## 🎯 PASOS PARA DESPLEGAR AHORA:

### PASO 1: Desplegar Backend en Vercel

```bash
1. Ir a https://vercel.com/dashboard
2. Click "Add New" → "Project"
3. Importar el repositorio
4. Seleccionar "Other" como framework
5. Root Directory: backend/
6. Click Deploy
```

**Anota la URL que te da Vercel, ejemplo: `https://pati-backend-abc123.vercel.app`**

---

### PASO 2: Desplegar Frontend en Vercel

```bash
1. Ir a https://vercel.com/dashboard
2. Click "Add New" → "Project"
3. Importar el MISMO repositorio
4. Seleccionar "Angular" como framework
5. Root Directory: frontend/
6. Build Command: npm run build (detectado automáticamente)
7. Install Command: npm install
8. Output Directory: dist/pati-confeccion (automático)
9. Click Deploy
```

**Importante:** Los archivos se generarán en `dist/pati-confeccion/` (no en `dist/`)

---

### PASO 3: Conectar Frontend con Backend

**Backend ya desplegado en:** `https://confecciones-q7jq.vercel.app`

✅ Ya está configurado con REWRITES en `frontend/vercel.json`:
```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://confecciones-q7jq.vercel.app/api/:path*"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

✅ `environment.prod.ts` ya apunta a:
```typescript
apiUrl: 'https://confecciones-q7jq.vercel.app/api/v1'
```

---

### PASO 4: Configurar CORS en Backend

**Importante:** Después de desplegar el frontend, actualizar el CORS en el backend.

En Vercel Dashboard del backend (confecciones-q7jq):
```
Settings → Environment Variables

Actualizar/Agregar:
- FRONTEND_URL: https://confecciones-59k3.vercel.app (o tu URL de frontend)
- ENVIRONMENT: production

Luego: Deployments → Redeploy → Trigger deployment
```

**¡Crítico!** Sin esto, obtendrás error CORS en el navegador.

---

## ✨ Verifica que funciona:

1. Abre el frontend en el navegador
2. Abre DevTools (F12)
3. Ve a Network
4. Haz cualquier acción que haga una llamada API
5. Verifica que la request va a la URL correcta del backend

---

## 🐛 RESOLVIENDO ERROR CORS ACTUAL

**Error:** `Access to XMLHttpRequest at 'http://...' has been blocked by CORS policy`

**Solución:**

1. **En el backend Vercel (confecciones-q7jq.vercel.app):**
   - Settings → Environment Variables
   - Actualizar: `FRONTEND_URL=https://confecciones-59k3.vercel.app`
   - Verificar: `ENVIRONMENT=production`
   - Deployments → "Redeploy" (en el último deployment)

2. **En el código (ya arreglado):**
   - ✅ `colilla.service.ts` - Ahora usa `environment.apiUrl`
   - ✅ `config.py` - CORS permite Vercel URLs
   - Haz push al repositorio

3. **Esperar ~2 minutos** después del redeploy del backend

4. **Limpiar cache** en el navegador (Ctrl+Shift+Delete) o usar incógnito

## 🐛 Si hay error CORS persistente:

```bash
# En terminal local, verifica que el backend permite tu URL:
# Ir a backend Vercel → Logs

# Si ves: "No 'Access-Control-Allow-Origin' header"
# → El FRONTEND_URL no está configurado correctamente

# Solución rápida en Vercel:
Settings → Environment Variables
- FRONTEND_URL=https://confecciones-59k3.vercel.app
- Salvar cambios
- Deployments → Click en último deploy → Redeploy
```

---

## 📝 Para cambios futuros en desarrollo local:

```bash
# Terminal 1 - Backend:
cd backend
python -m venv venv
.\venv\Scripts\activate  # o source venv/bin/activate en Linux
pip install -r requirements.txt
python run_server.py  # Va a http://localhost:8001

# Terminal 2 - Frontend:
cd frontend
npm install
ng serve  # Va a http://localhost:4200
```

---

## 🔗 URLs después de desplegar:

- **Backend**: ✅ https://confecciones-q7jq.vercel.app
- **Frontend**: ✅ https://confecciones-59k3.vercel.app
- **API**: https://confecciones-q7jq.vercel.app/api/v1

¡Todo está desplegado! Solo resta configurar CORS ↑
