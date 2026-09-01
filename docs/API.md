# Documentación de la API - Sistema de Control Integral de Confección PATI

## Base URL

```
http://localhost:8000/api/v1
```

## Autenticación

Actualmente el sistema no requiere autenticación. En producción se recomienda implementar un sistema de autenticación.

## Endpoints

### Catálogo

#### Tallas

- `GET /catalogo/tallas` - Listar todas las tallas
- `POST /catalogo/tallas` - Crear una nueva talla
- `GET /catalogo/tallas/{id}` - Obtener una talla por ID
- `PUT /catalogo/tallas/{id}` - Actualizar una talla
- `DELETE /catalogo/tallas/{id}` - Eliminar una talla

#### Colores

- `GET /catalogo/colores` - Listar todos los colores
- `POST /catalogo/colores` - Crear un nuevo color
- `GET /catalogo/colores/{id}` - Obtener un color por ID
- `PUT /catalogo/colores/{id}` - Actualizar un color
- `DELETE /catalogo/colores/{id}` - Eliminar un color

#### Materiales

- `GET /catalogo/materiales` - Listar todos los materiales
- `POST /catalogo/materiales` - Crear un nuevo material
- `GET /catalogo/materiales/{id}` - Obtener un material por ID
- `PUT /catalogo/materiales/{id}` - Actualizar un material
- `DELETE /catalogo/materiales/{id}` - Eliminar un material

#### Referencias

- `GET /catalogo/referencias` - Listar todas las referencias
- `POST /catalogo/referencias` - Crear una nueva referencia
- `GET /catalogo/referencias/{id}` - Obtener una referencia por ID
- `PUT /catalogo/referencias/{id}` - Actualizar una referencia
- `DELETE /catalogo/referencias/{id}` - Eliminar una referencia

### Lotes

- `GET /lotes/` - Listar todos los lotes
  - Query params: `estado`, `es_pedido_especial`
- `POST /lotes/` - Crear un nuevo lote
- `GET /lotes/{id}` - Obtener un lote por ID
- `PUT /lotes/{id}` - Actualizar un lote
- `DELETE /lotes/{id}` - Eliminar un lote
- `GET /lotes/{id}/detalles` - Obtener detalles de un lote
- `PATCH /lotes/{id}/estado` - Actualizar estado de un lote

### Talleres

- `GET /talleres/` - Listar todos los talleres
  - Query params: `activo`
- `POST /talleres/` - Crear un nuevo taller
- `GET /talleres/{id}` - Obtener un taller por ID
- `PUT /talleres/{id}` - Actualizar un taller
- `DELETE /talleres/{id}` - Eliminar un taller

### Remisiones

- `GET /talleres/remisiones` - Listar todas las remisiones
  - Query params: `taller_id`, `estado`
- `POST /talleres/remisiones` - Crear una nueva remisión
- `GET /talleres/remisiones/{id}` - Obtener una remisión por ID
- `PUT /talleres/remisiones/{id}` - Actualizar una remisión
- `PATCH /talleres/remisiones/{id}/estado` - Actualizar estado de una remisión

### Producción

#### Avances

- `GET /produccion/avances` - Listar todos los avances
  - Query params: `lote_id`, `taller_id`
- `POST /produccion/avances` - Crear un nuevo avance
- `GET /produccion/avances/{id}` - Obtener un avance por ID
- `PUT /produccion/avances/{id}` - Actualizar un avance

#### Fallas

- `GET /produccion/fallas` - Listar todas las fallas
  - Query params: `lote_id`, `taller_id`, `estado`
- `POST /produccion/fallas` - Crear una nueva falla
- `GET /produccion/fallas/{id}` - Obtener una falla por ID
- `PUT /produccion/fallas/{id}` - Actualizar una falla

### Dashboard

- `GET /dashboard/estadisticas` - Obtener estadísticas generales
- `GET /dashboard/rendimiento-talleres` - Obtener rendimiento de talleres
- `GET /dashboard/lotes-prioridad` - Obtener lotes con prioridad

## Modelos de Datos

### Lote

```json
{
  "id": 1,
  "numero_lote": "LOTE-001",
  "referencia_id": 1,
  "color_id": 1,
  "material_id": 1,
  "estado": "en_corte",
  "fecha_corte": "2024-01-15T10:00:00Z",
  "fecha_asignacion": null,
  "observaciones": "Lote especial",
  "es_pedido_especial": false,
  "prioridad": 0,
  "created_at": "2024-01-15T10:00:00Z",
  "detalles": [
    {
      "id": 1,
      "talla_id": 1,
      "cantidad": 100,
      "cantidad_cortada": 0,
      "cantidad_en_taller": 0,
      "cantidad_confeccionada": 0,
      "cantidad_entregada": 0
    }
  ]
}
```

### Estados de Lote

- `en_corte` - En proceso de corte
- `corte_completado` - Corte completado
- `en_camino` - En camino al taller
- `en_taller` - En el taller
- `en_confeccion` - En proceso de confección
- `parcialmente_entregado` - Parcialmente entregado
- `completado` - Completado
- `cancelado` - Cancelado

### Estados de Remisión

- `pendiente` - Pendiente
- `en_transito` - En tránsito
- `recibida` - Recibida
- `parcialmente_entregada` - Parcialmente entregada
- `completada` - Completada
- `cancelada` - Cancelada

### Tipos de Falla

- `defecto_tela` - Defecto en la tela
- `defecto_confeccion` - Defecto en la confección
- `defecto_color` - Defecto en el color
- `defecto_talla` - Defecto en la talla
- `otro` - Otro tipo de falla

### Estados de Falla

- `reportada` - Reportada
- `en_revision` - En revisión
- `corregida` - Corregida
- `rechazada` - Rechazada

## Ejemplos de Uso

### Crear un Lote

```bash
curl -X POST "http://localhost:8000/api/v1/lotes/" \
  -H "Content-Type: application/json" \
  -d '{
    "numero_lote": "LOTE-001",
    "referencia_id": 1,
    "color_id": 1,
    "material_id": 1,
    "fecha_corte": "2024-01-15T10:00:00Z",
    "detalles": [
      {
        "talla_id": 1,
        "cantidad": 100
      },
      {
        "talla_id": 2,
        "cantidad": 150
      }
    ]
  }'
```

### Actualizar Estado de Lote

```bash
curl -X PATCH "http://localhost:8000/api/v1/lotes/1/estado" \
  -H "Content-Type: application/json" \
  -d '"corte_completado"'
```

### Crear una Remisión

```bash
curl -X POST "http://localhost:8000/api/v1/talleres/remisiones" \
  -H "Content-Type: application/json" \
  -d '{
    "numero_remision": "REM-001",
    "lote_id": 1,
    "taller_id": 1,
    "fecha_remision": "2024-01-16T10:00:00Z",
    "detalles": [
      {
        "talla_id": 1,
        "cantidad": 100
      }
    ]
  }'
```

## Documentación Interactiva

La documentación interactiva de la API está disponible en:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

