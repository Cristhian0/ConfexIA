#!/bin/bash
# Ejemplos de cURL para testear las Reglas de Negocio

# Base URL
BASE_URL="http://localhost:8000/api"

# ==========================================
# RN-1: NO CERRAR ORDEN SIN CALIDAD
# ==========================================

echo "=== RN-1: Intentar cerrar orden con calidad pendiente ==="

# Escenario: Intentar cambiar orden a completada cuando hay inspecciones pendientes
curl -X PATCH "${BASE_URL}/produccion/ordenes/1" \
  -H "Content-Type: application/json" \
  -d '{
    "estado": "completada"
  }'

# Respuesta esperada:
# HTTP 400 Bad Request
# {
#   "detail": "No se puede cerrar la orden. Existen inspecciones de calidad pendiente de clasificación."
# }


# ==========================================
# RN-2: NO DESPACHAR REMISIÓN SIN STOCK
# ==========================================

echo -e "\n\n=== RN-2: Intentar despachar remisión sin stock ==="

# Escenario: Crear remisión con estado despachada pero sin suficiente tela
curl -X POST "${BASE_URL}/taller/remisiones" \
  -H "Content-Type: application/json" \
  -d '{
    "numero_remision": "REM-2024-001",
    "lote_id": 1,
    "taller_id": 1,
    "estado": "despachada",
    "fecha_remision": "2026-04-04T10:00:00",
    "detalles": [
      {
        "material_id": 1,
        "color_id": 1,
        "cantidad_solicitada": 500
      }
    ]
  }'

# Respuesta esperada si no hay stock:
# HTTP 400 Bad Request
# {
#   "detail": "Stock insuficiente para material 1, color 1. Disponible: 300, Solicitado: 500"
# }


# ==========================================
# RN-3: NO METROS NEGATIVOS
# ==========================================

echo -e "\n\n=== RN-3: Intentar sacar más tela de la disponible ==="

# Escenario: Registrar salida que dejaría stock negativo
curl -X POST "${BASE_URL}/inventario-tela/rollos/salida" \
  -H "Content-Type: application/json" \
  -d '{
    "material_id": 1,
    "color_id": 1,
    "cantidad": 150,
    "orden_corte_id": 1,
    "descripcion": "Salida para corte"
  }'

# Respuesta esperada si cantidad actual < cantidad solicitada:
# HTTP 400 Bad Request
# {
#   "detail": "No se puede registrar salida. Stock actual: 100 metros, Intento de salida: 150 metros. 
#            Resultaría en -50 metros negativos."
# }


# ==========================================
# RN-4: RECALCULAR COSTO (AUTOMÁTICO)
# ==========================================

echo -e "\n\n=== RN-4: Registrar costo (recálculo automático) ==="

# Escenario: Crear registro financiero, sistema recalcula automáticamente
curl -X POST "${BASE_URL}/documentos/noc/5/financiero" \
  -H "Content-Type: application/json" \
  -d '{
    "noc_id": 5,
    "tipo_movimiento": "costo_tela",
    "monto": 5000,
    "descripcion": "Costo de tela comprada"
  }'

# Respuesta esperada:
# HTTP 201 Created
# {
#   "id": 123,
#   "noc_id": 5,
#   "tipo_movimiento": "costo_tela",
#   "monto": 5000,
#   ...
# }
# 
# NOTA: El costo unitario del lote se recalculó automáticamente
# Nueva fórmula: (Costo Tela + Insumos + Mano Obra) / Cantidad Total


# ==========================================
# RN-5: VARIANTE ÚNICA (PREPARADA)
# ==========================================

echo -e "\n\n=== RN-5: Validación de variante única (preparada) ==="

# Escenario futuro: Intentar crear dos variantes iguales
# POST /api/catalogo/variantes
# {
#   "producto_id": 1,
#   "color_id": 1,
#   "talla_id": 1,
#   "sku": "VAR-001"
# }
#
# Segunda llamada con mismos parámetros sería rechazada:
# HTTP 400 Bad Request
# {
#   "detail": "Ya existe una variante con esta combinación de producto, color y talla."
# }


# ==========================================
# RN-6: LOTE → PRODUCTO ÚNICO (PREPARADA)
# ==========================================

echo -e "\n\n=== RN-6: Un lote pertenece a un solo producto (preparada) ==="

# Escenario futuro: Intentar asignar lote a producto diferente
# PATCH /api/lotes-produccion/1
# {
#   "producto_id": 2
# }
#
# Si lote ya pertenece a producto 1:
# HTTP 400 Bad Request
# {
#   "detail": "El lote LOTE-001 ya está asignado al producto 1. No se puede cambiar a producto 2."
# }


# ==========================================
# RN-7: ACTUALIZAR PT AL APROBAR CALIDAD
# ==========================================

echo -e "\n\n=== RN-7: Actualizar PT al aprobar calidad (automático) ==="

# Escenario: Aprobar inspección de calidad, PT se actualiza automáticamente
curl -X PUT "${BASE_URL}/control-calidad/calidad/10" \
  -H "Content-Type: application/json" \
  -d '{
    "estado": "aprobado",
    "cantidad_aprobada": 100,
    "observaciones": "Prendas aprobadas para venta"
  }'

# Respuesta esperada:
# HTTP 200 OK
# {
#   "id": 10,
#   "lote_id": 5,
#   "estado": "aprobado",
#   "cantidad_aprobada": 100,
#   ...
# }
#
# NOTA: El inventario de Producto Terminado se actualizó automáticamente:
# InventarioPT.cantidad_disponible += 100


# ==========================================
# EJEMPLOS DE OPERACIONES VÁLIDAS
# ==========================================

echo -e "\n\n=== OPERACIONES VÁLIDAS (ACEPTADAS) ==="

echo "✅ 1. Ingresar tela a bodega (siempre válido)"
curl -X POST "${BASE_URL}/inventario-tela/rollos/ingreso" \
  -H "Content-Type: application/json" \
  -d '{
    "material_id": 1,
    "color_id": 1,
    "cantidad": 500,
    "lote_proveedor": "PROV-2024-001",
    "descripcion": "Ingreso de tela nuevaacuación"
  }'

echo -e "\n✅ 2. Crear orden de producción"
curl -X POST "${BASE_URL}/produccion/ordenes" \
  -H "Content-Type: application/json" \
  -d '{
    "lote_id": 1,
    "observaciones": "Orden de producción normal"
  }'

echo -e "\n✅ 3. Crear remisión sin despacho inmediato"
curl -X POST "${BASE_URL}/taller/remisiones" \
  -H "Content-Type: application/json" \
  -d '{
    "numero_remision": "REM-2024-002",
    "lote_id": 1,
    "taller_id": 1,
    "estado": "pendiente",
    "fecha_remision": "2026-04-04T10:00:00",
    "detalles": [
      {
        "material_id": 1,
        "color_id": 1,
        "cantidad_solicitada": 100
      }
    ]
  }'

# Respuesta esperada:
# HTTP 201 Created
# {
#   "id": 5,
#   "numero_remision": "REM-2024-002",
#   "estado": "pendiente",
#   ...
# }


# ==========================================
# CASOS DE PRUEBA RECOMENDADOS
# ==========================================

cat << 'EOF'

## PLAN DE PRUEBAS RECOMENDADO

### Test Suite 1: Reglas de Negocio
1. [ ] RN-1: Cierre sin calidad → HTTP 400
2. [ ] RN-2: Despacho sin stock → HTTP 400
3. [ ] RN-3: Salida negativa → HTTP 400
4. [ ] RN-4: Costo recalculado automáticamente
5. [ ] RN-7: PT actualizado al aprobar

### Test Suite 2: Casos Válidos
1. [ ] Ingresar tela → HTTP 201
2. [ ] Crear orden → HTTP 201
3. [ ] Crear remisión pendiente → HTTP 201
4. [ ] Salida con suficiente stock → HTTP 201

### Test Suite 3: Integración
1. [ ] Flujo completo: Ingreso → Remisión → Despacho → Calidad → PT
2. [ ] Verificar consistencia de datos en cada paso
3. [ ] Validar logs de auditoría

### Test Suite 4: Casos Límite
1. [ ] Stock exactamente igual a solicitado
2. [ ] Múltiples movimientos simultáneos
3. [ ] Actualización parcial de lotes

EOF

echo -e "\n\n=== SCRIPTS DE PRUEBA COMPLETADOS ==="
