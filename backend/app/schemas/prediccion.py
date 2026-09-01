"""Esquemas Pydantic para predicciones y análisis de IA"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class DatosHistoricos(BaseModel):
    """Datos históricos para entrenar modelos"""
    fecha: str
    cantidad: int
    producto_id: Optional[int] = None


class PrediccionDemanda(BaseModel):
    """Predicción individual de demanda"""
    fecha: str
    cantidad_predicha: float
    confianza: float


class RespuestaPredictorDemanda(BaseModel):
    """Respuesta del predictor de demanda"""
    predicciones: List[PrediccionDemanda]
    modelo_entrenado: bool
    dias_historicos: int
    nota: Optional[str] = None


class RegistroDefectos(BaseModel):
    """Registro de defectos para análisis"""
    cantidad_defectos: int
    porcentaje_rechazo: float
    horas_produccion: float
    lote_id: Optional[int] = None
    fecha: Optional[str] = None


class AnomaliaDetectada(BaseModel):
    """Anomalía detectada en datos"""
    indice: int
    severidad: float
    registro: dict


class RespuestaDetectorDefectos(BaseModel):
    """Respuesta del detector de defectos"""
    anomalias_detectadas: int
    anomalias: List[AnomaliaDetectada]
    registros_analizados: int
    modelo_entrenado: bool


class PuntoReorden(BaseModel):
    """Recomendación de punto de reorden"""
    punto_reorden: float
    stock_minimo: float
    stock_seguridad: float
    demanda_promedio: float
    lead_time_dias: int
    recomendacion: str


class CantidadEconomicaOrden(BaseModel):
    """Cantidad económica de orden (EOQ)"""
    cantidad_optima: float
    costo_anual_total: float
    numero_ordenes_ano: float
    dias_entre_ordenes: float


class InsightDashboard(BaseModel):
    """Insight para mostrar en dashboard"""
    titulo: str
    descripcion: str
    valor_principal: float
    unidad: str
    tipo_alerta: str  # 'info', 'warning', 'error', 'success'
    recomendacion: Optional[str] = None
    datos_adicionales: Optional[dict] = None


class AnaliseDatos(BaseModel):
    """Análisis completo de datos"""
    fecha_analisis: datetime
    predicciones_demanda: Optional[RespuestaPredictorDemanda] = None
    anomalias_calidad: Optional[RespuestaDetectorDefectos] = None
    recomendaciones_inventario: Optional[dict] = None
    insights: List[InsightDashboard] = []
