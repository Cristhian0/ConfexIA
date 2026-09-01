# 🚀 Guía Rápida - IA en 5 Minutos

## Instalación (1 minuto)

```bash
cd backend
pip install -r requirements.txt
```

## Generar datos de prueba (1 minuto)

```bash
python setup_ia_test_data.py
```

Verás algo así:
```
✅ 60 registros de demanda creados
✅ 100 registros de calidad creados
✅ Modelos entrenados correctamente
```

## Probar en navegador (2 minutos)

### 1. Iniciar servidor
```bash
python run_server.py
```

### 2. Ir a cualquiera de estos endpoints:

**Ver documentación interactiva:**
- http://localhost:8000/docs

**Probar predicción de demanda:**
- http://localhost:8000/api/v1/predicciones/demanda?dias=7

**Obtener insights completos:**
- http://localhost:8000/api/v1/predicciones/dashboard/insights

## Integrar en Angular (1 minuto)

En tu dashboard HTML:

```html
<app-ia-insights></app-ia-insights>
```

En tu módulo:
```typescript
import { IaInsightsComponent } from './components/dashboard/ia-insights/ia-insights.component';

@NgModule({
  declarations: [ IaInsightsComponent ]
})
export class AppModule { }
```

---

## 📊 Qué hace cada cosa

| Componente | Función | Endpoint |
|-----------|---------|----------|
| **Predictor** | Predice demanda futura | `/predicciones/demanda` |
| **Detector** | Detecta defectos anómalos | `/predicciones/defectos/detectar` |
| **Recomendador** | Calcula punto de reorden | `/predicciones/inventario/punto-reorden` |
| **Dashboard** | Muestra todo visualmente | `/predicciones/dashboard/insights` |

---

## 🎯 Próximos pasos

1. ✅ **Hecho:** Instalar y entrenar modelos
2. ⏭️ **Ahora:** Probar en navegador
3. ⏭️ **Luego:** Integrar componente Angular
4. ⏭️ **Final:** Usar predicciones en tu negocio

**¿Problemas?** Lee `IA_IMPLEMENTACION_COMPLETA.md` para documentación completa.

---

Hecho con ❤️ | Sistema de IA para gestión de confección textil
