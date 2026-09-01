# Guía de Usuario - Sistema de Control Integral de Confección PATI

## Introducción

Esta guía te ayudará a utilizar el sistema de control integral de confección de PATI. El sistema permite gestionar todo el proceso de producción desde el corte hasta la entrega final.

## Acceso al Sistema

1. Abrir el navegador web
2. Navegar a `http://localhost:4200`
3. El sistema mostrará el dashboard principal

## Estructura del Sistema

### Dashboard

El dashboard proporciona una vista general del estado de la producción:
- Estadísticas de prendas (total, en corte, en taller, confeccionadas, entregadas)
- Lotes por estado
- Resumen general (talleres activos, remisiones pendientes, fallas pendientes)
- Rendimiento de talleres
- Lotes con prioridad

### Gestión de Lotes

Los lotes representan un conjunto de prendas que se procesan juntas.

#### Crear un Lote

1. Navegar a "Lotes" en el menú lateral
2. Hacer clic en "Nuevo Lote"
3. Completar el formulario:
   - Número de lote (único)
   - Referencia
   - Color
   - Material
   - Fecha de corte
   - Prioridad (Normal, Alta, Urgente)
   - Marcar si es pedido especial
4. Agregar detalles por talla:
   - Seleccionar talla
   - Ingresar cantidad
   - Agregar más tallas si es necesario
5. Hacer clic en "Guardar"

#### Editar un Lote

1. En la lista de lotes, hacer clic en el icono de editar
2. Modificar los campos necesarios
3. Hacer clic en "Guardar"

#### Cambiar Estado de un Lote

Los estados de un lote se actualizan automáticamente según las acciones realizadas:
- **En Corte**: Estado inicial cuando se crea el lote
- **Corte Completado**: Se actualiza cuando se completa el corte
- **En Camino**: Cuando se crea una remisión
- **En Taller**: Cuando la remisión es recibida
- **En Confección**: Cuando hay avances de producción
- **Parcialmente Entregado**: Cuando se entrega parcialmente
- **Completado**: Cuando todas las prendas están entregadas

### Gestión de Talleres

Los talleres son las entidades que realizan la confección.

#### Crear un Taller

1. Navegar a "Talleres" en el menú lateral
2. Hacer clic en "Nuevo Taller"
3. Completar el formulario:
   - Código del taller
   - Nombre
   - Dirección
   - Teléfono
   - Contacto
   - Capacidad diaria
4. Hacer clic en "Guardar"

### Gestión de Remisiones

Las remisiones son los documentos que se envían a los talleres con los lotes asignados.

#### Crear una Remisión

1. Navegar a "Remisiones" en el menú lateral
2. Hacer clic en "Nueva Remisión"
3. Completar el formulario:
   - Número de remisión (único)
   - Lote a remitir
   - Taller destino
   - Fecha de remisión
   - Fecha de entrega estimada
4. Agregar detalles por talla:
   - Seleccionar talla
   - Ingresar cantidad a remitir
5. Hacer clic en "Guardar"

#### Actualizar Estado de Remisión

1. En la lista de remisiones, seleccionar la remisión
2. Cambiar el estado según corresponda:
   - **Pendiente**: Recién creada
   - **En Tránsito**: Enviada al taller
   - **Recibida**: Recibida por el taller
   - Esto actualiza automáticamente el estado del lote a "En Taller"
   - **Parcialmente Entregada**: Entregada parcialmente
   - **Completada**: Completamente entregada

### Control de Producción

#### Registrar Avance de Producción

1. Navegar a "Producción" en el menú lateral
2. Seleccionar "Registrar Avance"
3. Completar el formulario:
   - Lote
   - Taller
   - Remisión (opcional)
   - Fecha del avance
   - Cantidad de avance
   - Porcentaje de avance
   - Observaciones
4. Hacer clic en "Guardar"

El sistema actualiza automáticamente:
- La cantidad confeccionada en el lote
- El estado del lote según el progreso

#### Reportar Falla de Confección

1. Navegar a "Producción" en el menú lateral
2. Seleccionar "Reportar Falla"
3. Completar el formulario:
   - Lote afectado
   - Taller (opcional)
   - Tipo de falla
   - Cantidad afectada
   - Descripción detallada
   - Fecha del reporte
4. Hacer clic en "Guardar"

#### Gestionar Fallas

1. Ver la lista de fallas reportadas
2. Para cada falla, puedes:
   - Cambiar el estado a "En Revisión"
   - Agregar acción correctiva
   - Marcar como "Corregida" cuando se resuelva
   - Rechazar si no aplica

### Catálogo

El catálogo permite gestionar los datos maestros del sistema.

#### Tallas

1. Navegar a "Catálogo" > "Tallas"
2. Crear, editar o eliminar tallas
3. Cada talla tiene:
   - Código (único)
   - Nombre
   - Estado (activo/inactivo)

#### Colores

1. Navegar a "Catálogo" > "Colores"
2. Crear, editar o eliminar colores
3. Cada color tiene:
   - Código (único)
   - Nombre
   - Estado (activo/inactivo)

#### Materiales

1. Navegar a "Catálogo" > "Materiales"
2. Crear, editar o eliminar materiales
3. Cada material tiene:
   - Código (único)
   - Nombre
   - Descripción
   - Estado (activo/inactivo)

#### Referencias

1. Navegar a "Catálogo" > "Referencias"
2. Crear, editar o eliminar referencias
3. Cada referencia tiene:
   - Código (único)
   - Nombre
   - Descripción
   - Indicador de pedido especial
   - Estado (activo/inactivo)

## Flujo de Trabajo Típico

### 1. Configuración Inicial

1. Configurar catálogos:
   - Crear tallas (S, M, L, XL, etc.)
   - Crear colores
   - Crear materiales
   - Crear referencias de prendas

2. Registrar talleres:
   - Crear los talleres que realizarán la confección

### 2. Proceso de Producción

1. **Crear Lote**:
   - Cuando el corte termina, crear un lote con los datos del corte
   - Incluir todas las tallas y cantidades

2. **Crear Remisión**:
   - Asignar el lote a un taller mediante una remisión
   - Especificar qué tallas y cantidades se envían

3. **Recibir Remisión**:
   - Cuando el taller recibe la remisión, actualizar el estado a "Recibida"

4. **Registrar Avances**:
   - A medida que el taller avanza, registrar los avances de producción
   - El sistema actualiza automáticamente las cantidades

5. **Reportar Fallas** (si aplica):
   - Si hay problemas en la confección, reportar las fallas
   - Seguir el proceso de corrección

6. **Completar Producción**:
   - Cuando todas las prendas están listas, el sistema marca el lote como completado

## Consejos y Mejores Prácticas

1. **Nomenclatura Consistente**: Usar códigos consistentes para lotes, remisiones, etc.
2. **Actualizar Estados**: Mantener los estados actualizados para tener visibilidad real
3. **Registrar Avances Regularmente**: Registrar avances periódicamente para tener información actualizada
4. **Documentar Fallas**: Describir detalladamente las fallas para facilitar la corrección
5. **Revisar Dashboard**: Revisar el dashboard regularmente para identificar cuellos de botella

## Solución de Problemas

### No puedo crear un lote
- Verificar que los catálogos estén configurados (referencia, color, material, tallas)
- Verificar que el número de lote sea único

### No puedo crear una remisión
- Verificar que el lote exista
- Verificar que el taller exista
- Verificar que las cantidades no excedan las del lote

### Los estados no se actualizan
- Verificar que las acciones se completen correctamente
- Algunos estados se actualizan automáticamente, otros requieren acción manual

## Soporte

Para más información, consultar:
- [Guía de Instalación](INSTALLATION.md)
- [Documentación de la API](API.md)

