# Guía Rápida de Reglas de Negocio Implementadas

## 📋 Resumen de las 7 Reglas

| # | Regla | Estado | Endpoint | Archivo |
|---|-------|--------|----------|---------|
| 1 | ❌ No cerrar orden sin calidad | ✅ Implementada | PATCH `/ordenes/{id}` | `produccion.py` |
| 2 | ❌ No despachar sin stock | ✅ Implementada | POST `/remisiones` | `taller.py` |
| 3 | ❌ No metros negativos | ✅ Implementada | POST `/rollos/salida` | `inventario_tela.py` |
| 4 | 🔄 Recalcular costo | ✅ Implementada | POST `/noc/{id}/financiero` | `documentos.py` |
| 5 | 🔐 Variante única | ✅ Preparada | - | `business_rules.py` |
| 6 | 🔗 Lote → Producto | ✅ Preparada | - | `lotes_produccion.py` |
| 7 | 📦 Actualizar PT | ✅ Implementada | PUT `/calidad/{id}` | `control_calidad.py` |

---

## 🔧 Cómo Funciona

### Validaciones Activas Ahora

#### RN-1: Cierre de Orden de Producción
```bash
# ❌ Esto será rechazado:
PATCH /api/produccion/ordenes/5
{
    "estado": "completada"  # Si hay inspecciones pendientes
}

# ✅ Respuesta de error:
HTTP 400
{
    "detail": "No se puede cerrar la orden. Existen inspecciones de calidad pendiente."
}
```

#### RN-2: Validación de Stock
```bash
# ❌ Esto será rechazado:
POST /api/taller/remisiones
{
    "estado": "despachada",
    "detalles": [{"material_id": 1, "color_id": 2, "cantidad": 500}]
}

# ✅ Si no hay suficiente stock:
HTTP 400
{
    "detail": "Stock insuficiente para material 1, color 2. Disponible: 300, Solicitado: 500"
}
```

#### RN-3: Metros Positivos
```bash
# ❌ Esto será rechazado:
POST /api/inventario-tela/rollos/salida
{
    "material_id": 1,
    "color_id": 2,
    "cantidad": 150  # Si solo hay 100 metros
}

# ✅ Respuesta de error:
HTTP 400
{
    "detail": "No se puede registrar salida. Resultaría en -50 metros negativos."
}
```

#### RN-4: Recálculo Automático de Costo
```bash
# ✅ Cuando se crea un registro financiero:
POST /api/documentos/noc/3/financiero
{
    "tipo_movimiento": "costo_tela",
    "monto": 1000
}

# El sistema automáticamente recalcula:
# Costo Unitario = (Costo Tela + Insumos + Mano de Obra) / Cantidad Total
```

#### RN-7: Actualización de Inventario PT
```bash
# ✅ Cuando se aprueba calidad:
PUT /api/control-calidad/calidad/15
{
    "estado": "aprobado",
    "cantidad_aprobada": 100
}

# El sistema automáticamente actualiza:
# InventarioPT.cantidad_disponible += 100
```

---

## 📂 Estructura de Código

### Archivo Principal
**`app/core/business_rules.py`** - Centraliza todas las reglas

Importar en cualquier endpoint:
```python
from app.core.business_rules import (
    validar_cierre_orden_produccion,
    validar_stock_disponible_remision,
    validar_metros_positivos_tela,
    recalcular_costo_unitario_lote,
    actualizar_inventario_pt_por_calidad
)
```

### Endpoints Modificados
1. ✅ `app/api/produccion.py` - Línea ~74
2. ✅ `app/api/taller.py` - Línea ~55
3. ✅ `app/api/inventario_tela.py` - Línea ~116
4. ✅ `app/api/documentos.py` - Línea ~121
5. ✅ `app/api/control_calidad.py` - Línea ~92
6. ✅ `app/api/lotes_produccion.py` - Línea ~1 (importación)

---

## 🛡️ Protecciones Activas

| Escenario | Protección | Resultado |
|-----------|------------|-----------|
| Cerrar orden con QC pendiente | RN-1 | ❌ Rechazado HTTP 400 |
| Despachar sin stock | RN-2 | ❌ Rechazado HTTP 400 |
| Salida de tela negativa | RN-3 | ❌ Rechazado HTTP 400 |
| Cambiar costos | RN-4 | 🔄 Recalcula automáticamente |
| Aprobar en calidad | RN-7 | 📦 Actualiza PT automáticamente |

---

## 🔌 Integración

Todas las reglas están integradas en:
- ✅ Layer de validación (business_rules.py)
- ✅ Endpoints (produccion.py, taller.py, etc.)
- ✅ Transacciones con rollback en caso de error
- ✅ Logging de errores (sin bloquear operación)

---

## 📊 Flujo de Ejecución

```
Cliente hace REQUEST
        ↓
    ↓ Endpoint API
        ↓
    ↓ Validación de entrada
        ↓
    ↓ Validación de RN (business_rules.py)
        ↓
    ¿Válido? ─→ NO ──→ HTTP 400 + Mensaje de error
        │
        YES
        ↓
    ✅ Procesar cambios
        ↓
    ✅ Actualizar automáticamente (RN-4, RN-7)
        ↓
    ✅ Guardar en BD
        ↓
    ✅ Retornar HTTP 200/201
```

---

## 🚨 Manejo de Errores

### Errores de Validación (HTTP 400)
Cuando viola una regla de negocio:
```json
{
    "detail": "Descripción específica del error"
}
```

### Errores de Recurso (HTTP 404)
Cuando no encuentra recurso:
```json
{
    "detail": "Orden de producción no encontrada"
}
```

### Errores de Sistema (HTTP 500)
Fallidas no esperadas (raras):
```json
{
    "detail": "Error interno del servidor"
}
```

---

## 🎯 Próximas Fases

- [ ] Agregar pruebas unitarias para cada regla
- [ ] Crear dashboard de cumplimiento
- [ ] Implementar alertas en tiempo real
- [ ] Audit trail completo
- [ ] Documentación Swagger actualizada

---

## 📞 Soporte Técnico

Si un usuario intenta violar una regla:
1. El sistema retorna un error específico
2. El frontend puede mostrar un mensaje amigable
3. Los logs registran el intento (si es necesario auditoría)

**Regla violated → Clear error message → User corrects → Retry ✅**
