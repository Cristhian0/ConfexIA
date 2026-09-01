# Error 404: Inventario de Tela - Salida de Rollos

## Problema
El endpoint `POST http://localhost:8001/api/v1/inventario-tela/rollos/salida` devuelve un error 404 (No encontrado).

## Causa
El servidor backend de FastAPI no está ejecutándose en el puerto 8001, o está ejecutándose en un puerto diferente.

## Solución

### 1. Verifica que el backend está corriendo
Abre una terminal en `c:\Users\Admin\trabjo\backend` y ejecuta:

```bash
cd c:\Users\Admin\trabjo\backend
python.exe -m uvicorn app.main:app --reload --port 8001
```

El servidor debe mostrar algo como:
```
Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
```

### 2. Verifica la conectividad
En otra terminal, prueba:
```bash
# En PowerShell
Invoke-WebRequest http://localhost:8001/health -UseBasicParsing
```

Deberías recibir una respuesta con estado 200 y body `{"status":"healthy"}`.

### 3. Verifica que el endpoint existe
```bash
Invoke-WebRequest http://localhost:8001/docs -UseBasicParsing
```

Esto abre la documentación interactiva de FastAPI. Busca "inventario-tela" y verifica que está el endpoint `/rollos/salida`.

### 4. Haz una prueba manual
Puedes usar PowerShell para probar la salida:

```powershell
$body = @{
    material_id = 1
    color_id = 1
    cantidad = 10
    orden_corte_id = $null
    descripcion = "Prueba"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8001/api/v1/inventario-tela/rollos/salida" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

## Notas importantes

- El backend debe estar corriendo **mientras** el frontend está en uso
- Usa el Puerto 8001 para el backend (como está en `environment.ts`)
- La aplicación Angular intenta conectarse a `http://localhost:8001/api/v1` automáticamente
