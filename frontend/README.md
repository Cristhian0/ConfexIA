# Frontend - Sistema de Control Integral de Confección PATI

## Descripción

Frontend desarrollado en Angular para el sistema de control integral de confección de PATI.

## Instalación

```bash
npm install
```

## Desarrollo

```bash
ng serve
```

La aplicación estará disponible en `http://localhost:4200`

## Build

```bash
ng build
```

Los archivos compilados estarán en `dist/pati-confeccion`

## Estructura

- `src/app/components/` - Componentes de la aplicación
- `src/app/services/` - Servicios HTTP
- `src/app/models/` - Modelos TypeScript
- `src/environments/` - Configuración de entornos

## Configuración

Editar `src/environments/environment.ts` para configurar la URL de la API:

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1'
};
```

