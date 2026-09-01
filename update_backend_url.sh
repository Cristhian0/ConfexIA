#!/bin/bash

# Script para actualizar automáticamente la URL del backend en la configuración

# Uso: ./update_backend_url.sh https://your-backend-app.vercel.app

if [ -z "$1" ]; then
    echo "Uso: ./update_backend_url.sh <BACKEND_URL>"
    echo "Ejemplo: ./update_backend_url.sh https://pati-backend.vercel.app"
    exit 1
fi

BACKEND_URL=$1

# Actualizar environment.prod.ts
echo "Actualizando environment.prod.ts..."
cd frontend
cat > src/environments/environment.prod.ts << EOF
export const environment = {
  production: true,
  apiUrl: '${BACKEND_URL}/api/v1'
};
EOF

# Actualizar vercel.json del frontend
echo "Actualizando vercel.json del frontend..."
cat > vercel.json << EOF
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "${BACKEND_URL}/api/:path*"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
EOF

echo "✅ Configuración actualizada"
echo "Backend URL: ${BACKEND_URL}"
echo "Frontend API URL: ${BACKEND_URL}/api/v1"
