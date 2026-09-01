## 🤖 Guía Completa - Sistema de IA e Inteligencia Artificial

Tu proyecto ahora tiene un **sistema completo de Machine Learning** integrado. Esta guía te explica qué se agregó y cómo usarlo.

---

## 📦 ¿Qué se Instaló?

### Backend (Python)

#### Librerías añadidas a `requirements.txt`:
- **scikit-learn** (1.3.2): Machine Learning
- **numpy** (1.24.3): Cálculos numéricos
- **statsmodels** (0.14.0): Series de tiempo
- **joblib** (1.3.2): Persistencia de modelos

#### Módulos nuevos:
1. **`backend/core/ml_models.py`** - Modelos de ML
   - `PredictorDemanda`: Predice demanda futura
   - `DetectorDefectos`: Detecta anomalías en calidad
   - `RecomendadorInventario`: Optimiza niveles de inventario

2. **`backend/app/api/predicciones.py`** - API REST
   - 7 endpoints nuevos para predicciones
   - Integración con base de datos
   - Análisis inteligente para dashboard

3. **`backend/app/schemas/prediccion.py`** - Validación de datos
   - Esquemas Pydantic para todas las predicciones

### Frontend (Angular)

1. **`frontend/src/app/services/predicciones.service.ts`**
   - Servicio para consumir API de IA
   - Métodos tipados y seguros
   - Cachéo automático de peticiones

2. **`frontend/src/app/components/dashboard/ia-insights/`**
   - Componente visual completo
   - Muestra predicciones en tiempo real
   - Panel de control inteligente

---

## 🚀 Primeros Pasos

### 1. Instalar dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 2. Generar datos de prueba y entrenar modelos

```bash
# Desde la carpeta backend
python setup_ia_test_data.py
```

**Output esperado:**
```
============================================================
🚀 GENERADOR DE DATOS DE PRUEBA - IA
============================================================

🗑️  Limpiando datos previos...
   ✅ Datos limpios

📊 Generando 60 días de datos de demanda...
✅ 60 registros de demanda creados

📋 Generando 100 registros de calidad...
✅ 100 registros de calidad creados

🤖 Entrenando modelos de IA...

1️⃣ Entrenando predictor de demanda...
   ✅ Predictor de demanda: Entrenado
   📈 Registros usados: 60

2️⃣ Entrenando detector de defectos...
   ✅ Detector de defectos: Entrenado
   📊 Registros usados: 100

3️⃣ Calculando recomendaciones de inventario...
   📍 Punto de reorden: 875
   🔒 Stock de seguridad: 45
   💡 Recomendación: Reordenar cuando stock <= 875
```

---

## 📊 Módulos Explicados

### 1. **Predictor de Demanda**

**¿Qué hace?**
- Analiza histórico de órdenes
- Predice demanda para los próximos 7-30 días
- Usa Random Forest + features de series de tiempo

**Cómo funciona:**
```python
# Backend automático
POST /api/v1/predicciones/entrenar/demanda  # Entrena modelo
GET  /api/v1/predicciones/demanda?dias=7   # Obtiene predicción
```

**Respuesta ejemplo:**
```json
{
  "predicciones": [
    {
      "fecha": "2026-06-12",
      "cantidad_predicha": 145.5,
      "confianza": 0.85
    },
    {
      "fecha": "2026-06-13",
      "cantidad_predicha": 152.3,
      "confianza": 0.82
    }
  ],
  "modelo_entrenado": true,
  "dias_historicos": 60
}
```

**Features utilizados:**
- Día de la semana
- Mes
- Promedio móvil 7 días
- Lag features (valores anteriores)

---

### 2. **Detector de Defectos**

**¿Qué hace?**
- Identifica patrones anómalos en QA
- Detecta defectos inesperados
- Usa Isolation Forest (no supervisado)

**Cómo funciona:**
```python
POST /api/v1/predicciones/entrenar/defectos      # Entrena
POST /api/v1/predicciones/defectos/detectar      # Detecta anomalías
```

**Respuesta ejemplo:**
```json
{
  "anomalias_detectadas": 2,
  "anomalias": [
    {
      "indice": 5,
      "severidad": 0.92,
      "registro": {
        "cantidad_defectos": 8,
        "colilla_id": 42
      }
    }
  ],
  "registros_analizados": 50,
  "modelo_entrenado": true
}
```

**Features analizados:**
- Cantidad de defectos
- Porcentaje de rechazo
- Horas de producción

---

### 3. **Recomendador de Inventario**

**¿Qué hace?**
- Calcula punto de reorden óptimo
- Recomienda cantidad de orden económica (EOQ)
- Basa cálculos en teoría estadística

**Fórmulas utilizadas:**

**Punto de Reorden:**
```
Punto de Reorden = (Demanda Promedio × Lead Time) + Stock Seguridad
Stock Seguridad = Factor Seguridad × Desviación Estándar × √(Lead Time)
```

**Cantidad Económica de Orden (EOQ):**
```
EOQ = √(2 × Demanda Anual × Costo Orden / Costo Mantenimiento)
```

**Endpoints:**
```python
POST /api/v1/predicciones/inventario/punto-reorden
POST /api/v1/predicciones/inventario/cantidad-economica
```

**Ejemplo de respuesta:**
```json
{
  "punto_reorden": 875,
  "stock_minimo": 830,
  "stock_seguridad": 45,
  "demanda_promedio": 166,
  "lead_time_dias": 5,
  "recomendacion": "Reordenar cuando stock <= 875"
}
```

---

## 🔗 Integración con Angular

### Usando el servicio de predicciones

```typescript
import { PrediccionesService } from './services/predicciones.service';

export class MiComponente implements OnInit {
  constructor(private predService: PrediccionesService) {}

  ngOnInit() {
    // Obtener todos los insights
    this.predService.obtenerInsights().subscribe(analisis => {
      console.log('Predicciones:', analisis.predicciones_demanda);
      console.log('Anomalías:', analisis.anomalias_calidad);
      console.log('Inventario:', analisis.recomendaciones_inventario);
      console.log('Insights:', analisis.insights);
    });
  }

  // Predicción individual de demanda
  predecirDemanda() {
    this.predService.predecirDemanda(7, 30).subscribe(resultado => {
      console.log('Demanda predicha:', resultado);
    });
  }

  // Detectar anomalías
  detectarProblemas() {
    this.predService.detectarAnomalias().subscribe(resultado => {
      console.log('Anomalías encontradas:', resultado.anomalias_detectadas);
    });
  }

  // Calcular reorden
  calcularReorden() {
    this.predService.calcularPuntoReorden(
      150,    // demanda promedio
      5,      // lead time (días)
      20,     // desviación estándar
      1.65    // factor de seguridad
    ).subscribe(reorden => {
      console.log('Punto de reorden:', reorden.punto_reorden);
    });
  }
}
```

---

## 🎨 Componente Visual (Dashboard)

El componente `IaInsightsComponent` ya está listo para usarse:

### Integrar en tu dashboard

```html
<!-- dashboard.component.html -->
<app-ia-insights></app-ia-insights>
```

### Declarar en módulo

```typescript
// app.module.ts
import { IaInsightsComponent } from './components/dashboard/ia-insights/ia-insights.component';

@NgModule({
  declarations: [
    IaInsightsComponent
  ]
})
export class AppModule { }
```

---

## 📋 API Endpoints Disponibles

### Predicción de Demanda

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/predicciones/entrenar/demanda` | Entrena modelo con datos históricos |
| GET | `/api/v1/predicciones/demanda?dias=7&dias_historicos=30` | Predice demanda futura |

### Detección de Defectos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/predicciones/entrenar/defectos` | Entrena detector de anomalías |
| POST | `/api/v1/predicciones/defectos/detectar` | Detecta anomalías en registros |

### Gestión de Inventario

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/predicciones/inventario/punto-reorden` | Calcula punto de reorden |
| POST | `/api/v1/predicciones/inventario/cantidad-economica` | Calcula EOQ |

### Dashboard Inteligente

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/predicciones/dashboard/insights` | Obtiene análisis completo |

---

## 🧪 Ejemplos de Uso con cURL

### 1. Entrenar predictor de demanda
```bash
curl -X POST http://localhost:8000/api/v1/predicciones/entrenar/demanda
```

### 2. Obtener predicción
```bash
curl -X GET "http://localhost:8000/api/v1/predicciones/demanda?dias=7&dias_historicos=30"
```

### 3. Calcular punto de reorden
```bash
curl -X POST "http://localhost:8000/api/v1/predicciones/inventario/punto-reorden" \
  -H "Content-Type: application/json" \
  -d '{"demanda_promedio": 150, "lead_time_dias": 5}'
```

### 4. Obtener insights completos
```bash
curl -X GET http://localhost:8000/api/v1/predicciones/dashboard/insights
```

---

## 🎯 Casos de Uso Prácticos

### Caso 1: Predecir demanda para la próxima semana

```typescript
// En tu componente
this.predService.predecirDemanda(7).subscribe(prediccion => {
  const demandaPromedio = prediccion.predicciones.reduce(
    (sum, p) => sum + p.cantidad_predicha, 0
  ) / prediccion.predicciones.length;
  
  console.log(`Demanda promedio estimada: ${demandaPromedio} unidades`);
});
```

### Caso 2: Alertar sobre defectos anómalos

```typescript
// Monitor de calidad
setInterval(() => {
  this.predService.detectarAnomalias().subscribe(resultado => {
    if (resultado.anomalias_detectadas > 0) {
      this.mostrarAlerta(
        `⚠️ Se detectaron ${resultado.anomalias_detectadas} anomalías`
      );
    }
  });
}, 5 * 60 * 1000); // Cada 5 minutos
```

### Caso 3: Gestión automática de inventario

```typescript
// Calcular reorden automático
const calculoReorden = async () => {
  const demandaHistorica = await this.obtenerDemandaHistorica();
  const demandaPromedio = promedio(demandaHistorica);
  const desviacion = desviacionEstandar(demandaHistorica);
  
  this.predService.calcularPuntoReorden(
    demandaPromedio,
    5,      // lead time
    desviacion
  ).subscribe(reorden => {
    // Guardar en base de datos
    this.guardarReorden(reorden);
  });
};
```

---

## 📈 Mejoras Futuras

### Próximas versiones podrían incluir:

1. **Deep Learning**
   - LSTM para series de tiempo más complejas
   - Redes neuronales para patrones no lineales

2. **Integración externa**
   - OpenAI GPT para insights textuales
   - Prophet de Facebook para forecasting avanzado

3. **Análisis avanzado**
   - Clustering de productos similares
   - Segmentación de clientes
   - Análisis de causas raíz

4. **Automatización**
   - Órdenes automáticas cuando hay alerta
   - Reentrenamiento automático de modelos
   - Feedback loop de precisión

---

## 🔧 Troubleshooting

### Error: `ModuleNotFoundError: No module named 'sklearn'`
```bash
pip install scikit-learn numpy statsmodels joblib
```

### Modelo no está entrenado
- Ejecuta: `python setup_ia_test_data.py`
- Asegúrate de tener suficientes datos históricos (mínimo 10-20 registros)

### Predicciones con baja confianza
- Aumenta los datos históricos (60+ días es ideal)
- Verifica que los datos sean realistas

### Endpoint lento
- Los modelos se cachean en memoria
- Primera predicción puede tardar más
- Aumenta la capacidad del servidor si es necesario

---

## 📚 Documentación Técnica

### Estructura de archivos nuevo

```
backend/
├── core/
│   └── ml_models.py              # 🆕 Modelos ML
├── app/
│   ├── api/
│   │   └── predicciones.py       # 🆕 Endpoints IA
│   └── schemas/
│       └── prediccion.py         # 🆕 Esquemas
└── models/
    └── (carpeta nuevo)           # 🆕 Persistencia de modelos

frontend/
├── src/app/
│   ├── services/
│   │   └── predicciones.service.ts       # 🆕 Servicio
│   └── components/dashboard/
│       └── ia-insights/                  # 🆕 Componente visual
│           ├── ia-insights.component.ts
│           ├── ia-insights.component.html
│           └── ia-insights.component.scss
```

---

## 🎓 Conceptos Clave

### Random Forest (Predictor de Demanda)
- Ensemble de árboles de decisión
- Ideal para relaciones no-lineales
- Robusta ante outliers

### Isolation Forest (Detector de Defectos)
- Detecta anomalías sin supervisión
- Eficiente en dimensiones altas
- No requiere etiquetado

### EOQ (Economic Order Quantity)
- Minimiza costos totales
- Balance entre orden y mantenimiento
- Bien conocido en logística

---

## ✅ Checklist de Implementación

- [x] Instalar librerías de ML
- [x] Crear módulo de modelos
- [x] Crear API endpoints
- [x] Crear esquemas Pydantic
- [x] Crear servicio Angular
- [x] Crear componente visual
- [x] Crear script de datos de prueba
- [x] Documentación completa

**¡Tu sistema de IA está listo para producción! 🚀**

---

## 📞 Soporte

Para problemas:
1. Revisa los logs: `backend/logs/`
2. Valida los datos: `python test_query.py`
3. Consulta la documentación: `/docs/API.md`

¡Que disfrutes el poder de la IA en tu sistema! 🤖
