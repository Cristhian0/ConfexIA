"""
Módulo de modelos de Machine Learning para predicciones
Versión simplificada que NO requiere compilación de C++
- Predicción de demanda
- Detección de defectos
- Recomendaciones de inventario
"""

import numpy as np
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
import statistics

# Rutas de almacenamiento de modelos
MODEL_DIR = Path(__file__).parent.parent / "models"
MODEL_DIR.mkdir(exist_ok=True)


class PredictorDemanda:
    """Predice demanda de productos para los próximos días - Versión simplificada"""
    
    def __init__(self):
        self.datos_historicos = []
        self.promedio = 100
        self.desviacion = 20
        self.entrenado = False
        self.model_path = MODEL_DIR / "predictor_demanda.json"
        self.cargar_si_existe()
    
    def entrenar(self, datos_historicos: list):
        """
        Entrena el modelo con datos históricos
        datos_historicos: [{'fecha': str, 'cantidad': int}, ...]
        """
        if not datos_historicos or len(datos_historicos) < 10:
            return False
        
        cantidades = [float(d.get('cantidad', 0)) for d in datos_historicos if d.get('cantidad')]
        
        if cantidades:
            self.promedio = statistics.mean(cantidades)
            self.desviacion = statistics.stdev(cantidades) if len(cantidades) > 1 else 20
            self.datos_historicos = cantidades[-30:]  # Últimos 30 registros
            self.entrenado = True
            self.guardar()
            return True
        
        return False
    
    def predecir(self, datos_recientes: list, dias=7) -> dict:
        """Predice demanda para los próximos N días usando promedio móvil"""
        if not datos_recientes:
            return self._prediccion_dummy(dias)
        
        cantidades = [float(d.get('cantidad', 0)) for d in datos_recientes if d.get('cantidad')]
        
        if cantidades:
            promedio_reciente = statistics.mean(cantidades[-7:]) if len(cantidades) >= 7 else statistics.mean(cantidades)
            desv = statistics.stdev(cantidades) if len(cantidades) > 1 else self.desviacion
        else:
            promedio_reciente = self.promedio
            desv = self.desviacion
        
        predicciones = []
        for i in range(dias):
            # Tendencia simple: añadir variación aleatoria controlada
            variacion = np.random.normal(0, desv * 0.3)  # Normal distribution
            cantidad = max(50, promedio_reciente + variacion)
            
            predicciones.append({
                "fecha": (datetime.now() + timedelta(days=i+1)).isoformat(),
                "cantidad_predicha": float(cantidad),
                "confianza": 0.75 + (0.1 if self.entrenado else 0)
            })
        
        return {
            "predicciones": predicciones,
            "modelo_entrenado": self.entrenado,
            "dias_historicos": len(datos_recientes)
        }
    
    def _prediccion_dummy(self, dias):
        """Retorna predicción dummy cuando no hay suficientes datos"""
        base = 100
        predicciones = []
        for i in range(dias):
            cantidad = base + np.random.randint(-20, 30)
            predicciones.append({
                "fecha": (datetime.now() + timedelta(days=i+1)).isoformat(),
                "cantidad_predicha": float(max(50, cantidad)),
                "confianza": 0.6
            })
        
        return {
            "predicciones": predicciones,
            "modelo_entrenado": False,
            "dias_historicos": 0,
            "nota": "Predicción - se necesitan más datos para mayor precisión"
        }
    
    def guardar(self):
        """Guarda el modelo a disco"""
        try:
            with open(self.model_path, 'w') as f:
                json.dump({
                    'promedio': self.promedio,
                    'desviacion': self.desviacion,
                    'entrenado': self.entrenado
                }, f)
        except Exception as e:
            print(f"Error guardando modelo: {e}")
    
    def cargar_si_existe(self):
        """Carga modelo si existe"""
        if self.model_path.exists():
            try:
                with open(self.model_path, 'r') as f:
                    data = json.load(f)
                    self.promedio = data.get('promedio', 100)
                    self.desviacion = data.get('desviacion', 20)
                    self.entrenado = data.get('entrenado', False)
            except Exception as e:
                print(f"Error cargando modelo: {e}")


class DetectorDefectos:
    """Detecta defectos anómalos en control de calidad - Versión simplificada"""
    
    def __init__(self):
        self.promedio_defectos = 0.5
        self.desviacion_defectos = 0.2
        self.entrenado = False
        self.model_path = MODEL_DIR / "detector_defectos.json"
        self.cargar_si_existe()
    
    def entrenar(self, datos_defectos: list):
        """Entrena detector con datos históricos"""
        if not datos_defectos or len(datos_defectos) < 20:
            return False
        
        cantidades_defectos = [float(d.get('cantidad_defectos', 0)) for d in datos_defectos]
        
        if cantidades_defectos:
            self.promedio_defectos = statistics.mean(cantidades_defectos)
            self.desviacion_defectos = statistics.stdev(cantidades_defectos) if len(cantidades_defectos) > 1 else 0.2
            self.entrenado = True
            self.guardar()
            return True
        
        return False
    
    def detectar_anomalias(self, nuevos_registros: list) -> dict:
        """Detecta registros anómalos usando desviación estándar"""
        if not nuevos_registros:
            return {
                "anomalias_detectadas": 0,
                "anomalias": [],
                "registros_analizados": 0,
                "modelo_entrenado": self.entrenado
            }
        
        anomalias = []
        umbral = self.promedio_defectos + (2 * self.desviacion_defectos)  # 2 sigma
        
        for idx, registro in enumerate(nuevos_registros):
            cantidad_defectos = float(registro.get('cantidad_defectos', 0))
            
            # Si está fuera de 2 desviaciones estándar, es anomalía
            if cantidad_defectos > umbral and self.entrenado:
                severidad = min(1.0, (cantidad_defectos - self.promedio_defectos) / max(self.desviacion_defectos, 0.1))
                anomalias.append({
                    "indice": idx,
                    "severidad": float(severidad),
                    "registro": registro
                })
        
        return {
            "anomalias_detectadas": len(anomalias),
            "anomalias": anomalias,
            "registros_analizados": len(nuevos_registros),
            "modelo_entrenado": self.entrenado
        }
    
    def guardar(self):
        """Guarda el modelo a disco"""
        try:
            with open(self.model_path, 'w') as f:
                json.dump({
                    'promedio_defectos': self.promedio_defectos,
                    'desviacion_defectos': self.desviacion_defectos,
                    'entrenado': self.entrenado
                }, f)
        except Exception as e:
            print(f"Error guardando modelo: {e}")
    
    def cargar_si_existe(self):
        """Carga modelo si existe"""
        if self.model_path.exists():
            try:
                with open(self.model_path, 'r') as f:
                    data = json.load(f)
                    self.promedio_defectos = data.get('promedio_defectos', 0.5)
                    self.desviacion_defectos = data.get('desviacion_defectos', 0.2)
                    self.entrenado = data.get('entrenado', False)
            except Exception as e:
                print(f"Error cargando modelo: {e}")


class RecomendadorInventario:
    """Recomienda niveles óptimos de inventario"""
    
    def __init__(self):
        self.modelo = LinearRegression()
        self.entrenado = False
        self.model_path = MODEL_DIR / "recomendador_inventario.pkl"
        self.cargar_si_existe()
    
    def calcular_punto_reorden(self, 
                               demanda_promedio: float, 
                               lead_time_dias: int,
                               desviacion_estandar: float,
                               factor_seguridad: float = 1.65) -> dict:
        """
        Calcula punto de reorden usando fórmula EOQ
        
        Punto de Reorden = (Demanda Promedio * Lead Time) + Stock Seguridad
        Stock Seguridad = Factor Seguridad * Desviación * sqrt(Lead Time)
        """
        
        if demanda_promedio <= 0:
            return {"punto_reorden": 0, "stock_minimo": 0, "recomendacion": "Datos inválidos"}
        
        # Demanda durante lead time
        demanda_lead_time = demanda_promedio * lead_time_dias
        
        # Stock de seguridad
        stock_seguridad = factor_seguridad * desviacion_estandar * (lead_time_dias ** 0.5)
        
        # Punto de reorden
        punto_reorden = demanda_lead_time + stock_seguridad
        
        return {
            "punto_reorden": float(round(punto_reorden)),
            "stock_minimo": float(round(demanda_lead_time)),
            "stock_seguridad": float(round(stock_seguridad)),
            "demanda_promedio": float(demanda_promedio),
            "lead_time_dias": lead_time_dias,
            "recomendacion": f"Reordenar cuando stock <= {round(punto_reorden)}"
        }
    
    def recomendar_cantidad_orden(self, 
                                  demanda_anual: float,
                                  costo_orden: float,
                                  costo_mantenimiento: float) -> dict:
        """
        Calcula cantidad económica de orden (EOQ)
        EOQ = sqrt(2*D*S / H)
        """
        
        if demanda_anual <= 0 or costo_orden <= 0 or costo_mantenimiento <= 0:
            return {"cantidad_optima": 0, "error": "Parámetros inválidos"}
        
        eoq = (2 * demanda_anual * costo_orden / costo_mantenimiento) ** 0.5
        
        return {
            "cantidad_optima": float(round(eoq)),
            "costo_anual_total": float(round(demanda_anual * costo_orden / eoq + eoq * costo_mantenimiento / 2)),
            "numero_ordenes_ano": float(round(demanda_anual / eoq)),
            "dias_entre_ordenes": float(round(365 / (demanda_anual / eoq)))
        }


# Instancias globales
predictor_demanda = PredictorDemanda()
detector_defectos = DetectorDefectos()
recomendador_inventario = RecomendadorInventario()
