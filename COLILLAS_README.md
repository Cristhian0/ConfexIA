# 📋 Módulo de Colillas de Confección

## Descripción

El módulo de **Colillas** permite gestionar tickets/recibos de confección para asignar trabajo a confeccionistas, registrar su progreso y generar documentos imprimibles en PDF.

## 🎯 Funcionalidades

### 1. **Crear Colillas**
- Asignar trabajo a confeccionistas desde un lote específico
- Definir tipo de trabajo (ensamble, costura, fileteado, terminación)
- Especificar cantidad de prendas
- Establecer fechas límite de entrega
- Agregar observaciones específicas

### 2. **Ver Colillas**
- **Por Confeccionista**: Agrupadas en paneles (total de prendas, completadas, rechazadas)
- **Listado Completo**: Tabla con todas las colillas, filtrable por estado/taller/lote
- **Estadísticas**: Porcentaje de completación por taller

### 3. **Imprimir/Descargar**
- PDF individual de colilla (formato 3.5" × 5.5" - tamaño ticket)
- PDF con resumen de todas las colillas de un taller
- PDF con resumen de todas las colillas de un lote
- Visualizar antes de descargar

### 4. **Registrar Progreso**
- Cambiar estado (Pendiente → En Proceso → Completada)
- Actualizar cantidad completada y rechazada
- Agregar observaciones al cambio de estado

### 5. **Importar desde PDF** (En desarrollo)
- Cargar un archivo PDF con colillas
- Procesamiento y creación automática de registros

## 🏗️ Estructura Backend

### Modelo de Datos


```python
# app/models/colilla.py
class Colilla(Base):
    numero_colilla      # Único: COL-TALLER-000001
    confeccionista_nombre
    confeccionista_cedula
    tipo_trabajo        # Enum: ensamble, costura, fileteado, terminacion
    cantidad_prendas    
    cantidad_completada
    cantidad_rechazada
    estado             # Enum: pendiente, en_proceso, completada, cancelada
    fecha_creacion
    fecha_limite_entrega
    fecha_completacion
    # Relaciones
    lote_id
    taller_id
    remision_detalle_id (opcional)
```

### Endpoints API

```
POST   /api/v1/colillas/                  # Crear
GET    /api/v1/colillas/                  # Listar (con filtros)
GET    /api/v1/colillas/{id}              # Obtener
PUT    /api/v1/colillas/{id}              # Actualizar
PATCH  /api/v1/colillas/{id}/estado       # Cambiar estado
DELETE /api/v1/colillas/{id}              # Eliminar
GET    /api/v1/colillas/por-confeccionista/{taller_id}  # Agrupadas
GET    /api/v1/colillas/stats/taller/{taller_id}       # Estadísticas
GET    /api/v1/colillas/pdf/{id}          # PDF individual
POST   /api/v1/colillas/pdf/taller/{id}   # PDF taller
POST   /api/v1/colillas/pdf/lote/{id}     # PDF lote
```

## 🎨 Estructura Frontend

### Componente: `ColillasComponent`

**Archivos:**
- `components/colillas/colillas.component.ts`
- `components/colillas/colillas.component.html`
- `components/colillas/colillas.component.scss`

**Modelo:** `models/colilla.model.ts`

**Servicio:** `services/colilla.service.ts`

### Tabs/Secciones

1. **Crear Colilla** - Formulario completo
2. **Por Confeccionista** - Vista agrupada
3. **Listado Completo** - Tabla con todas
4. **Importar PDF** - Carga de archivo

## 📦 Dependencias Instaladas

### Backend (`requirements.txt`)
```
reportlab==4.0.7   # Generación de PDFs
PyPDF2==3.0.1      # Procesamiento de PDFs
```

Instalar:
```bash
cd backend
pip install -r requirements.txt
```

## 🚀 Instalación y Configuración

### 1. Backend

El modelo ya está creado. Solo necesitas fazer migraciones:

```bash
cd backend
python migrate.py      # O tu script de migración
python run_server.py   # Iniciar servidor
```

El servidor estará en: `http://localhost:8000`

### 2. Frontend

El componente ya está integrado. Solo inicia el servidor Angular:

```bash
cd frontend
ng serve
```

La aplicación estará en: `http://localhost:4200`

Navega a `/colillas` para acceder al módulo.

## 📖 Casos de Uso

### Caso 1: Asignar Colilla a Confeccionista

1. Ve a **Crear Colilla**
2. Selecciona Lote y Taller
3. Ingresa nombre del confeccionista
4. Elige tipo de trabajo y cantidad de prendas
5. Define fecha límite
6. Clic en "Crear Colilla"
7. Genera PDF para entregar al confeccionista

### Caso 2: Seguimiento de Progreso

1. Ve a **Por Confeccionista** o **Listado Completo**
2. Visualiza estado actual
3. Haz clic en icono de Editar
4. Cambia a "Completada"
5. Ingresa cantidad completada/rechazada
6. Confirma cambio

### Caso 3: Reportes de Lote

1. Ve a **Listado Completo**
2. Filtra por Lote
3. Haz clic en "Descargar PDF (Lote)"
4. Recibe PDF con todas las colillas del lote

### Caso 4: Imprimir Colillas Individuales

1. Ve a **Por Confeccionista** o **Listado Completo**
2. Haz clic en icono PDF de la colilla
3. Se abre previsualización en navegador
4. Imprime o descarga desde el navegador

## 🎨 Personalización

### Cambiar Logo/Empresa en PDF

Editar `backend/app/utils/pdf_generator.py`:

```python
def generar_colilla_individual(colilla: Colilla, empresa_nombre: str = "Mi Empresa"):
    # Cambiar "Mi Empresa" por tu nombre
```

### Cambiar Tamaño de PDF

En `pdf_generator.py`:

```python
# Actualmente: Ticket 3.5" x 5.5"
ANCHO_PAGE = 3.5 * inch
ALTO_PAGE = 5.5 * inch

# Para A4 usar:
pagesize=letter  # o A4
```

### Modificar Template HTML

Editar `frontend/src/app/components/colillas/colillas.component.html`

## 🔍 Filtros Disponibles

| Filtro | Descripción |
|--------|-------------|
| Taller | Filtrar por taller específico |
| Lote | Filtrar por lote |
| Estado | Pendiente, En Proceso, Completada, Cancelada |
| Confeccionista | Búsqueda por nombre |

## 📊 Ejemplo de Datos en PDF

La colilla impresa incluye:

```
┌─────────────────────────────┐
│      COLILLA DE CONFECCIÓN  │
├─────────────────────────────┤
│ Colilla Nº: COL-TALL-000001 │
│ Fecha: 12/05/2026          │
│ Taller: Taller A            │
├─────────────────────────────┤
│ CONFECCIONISTA              │
│ Nombre: Juan Pérez          │
│ Cédula: 1234567890          │
├─────────────────────────────┤
│ DETALLES                    │
│ Tipo: Costura               │
│ Referencia: REF-001         │
│ Color: Azul                 │
│ Talla: L                    │
├─────────────────────────────┤
│ CANTIDADES                  │
│ A Confeccionar: 50          │
│ Completadas: 45             │
│ Rechazadas: 0               │
├─────────────────────────────┤
│ Fecha Límite: 15/05/2026    │
│ Estado: EN PROCESO          │
│ Observaciones: ...          │
├─────────────────────────────┤
│                             │
│ ________________            │
│ Firma del Confeccionista    │
└─────────────────────────────┘
```

## 🐛 Solución de Problemas

### "Error al crear colilla"
- Verifica que el Lote y Taller existan
- Comprueba que el confeccionista_nombre no esté vacío

### "Error al descargar PDF"
- Verifica que `reportlab` esté instalado: `pip install reportlab`
- Asegúrate que la colilla existe en la BD

### "La ruta /colillas no funciona"
- Reinicia el servidor Angular: `ng serve`
- Limpia caché del navegador

## 📝 Notas Importantes

- Los números de colilla se generan automáticamente: `COL-{CODIGO_TALLER}-{NÚMERO_SECUENCIAL}`
- El estado inicial siempre es **Pendiente**
- La fecha de completación se asigna automáticamente al marcar como Completada
- Se pueden crear múltiples colillas a la vez desde el endpoint `/lote/{id}`

## 🔮 Roadmap Futuro

- [ ] OCR en PDF cargados
- [ ] Firma digital
- [ ] Código QR en colillas
- [ ] WhatsApp integration para enviar colillas
- [ ] Dashboard con metas de producción
- [ ] Integración con sistema de costos (pago por pieza)
- [ ] Histórico de cambios por colilla
- [ ] Exportar a Excel
- [ ] Notificaciones por fecha límite próxima

## 📞 Soporte

Para reportar problemas o sugerencias, contacta al equipo de desarrollo.
