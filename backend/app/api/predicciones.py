"""
API de Predicciones e Inteligencia Artificial
Endpoints para:
- Predicción de demanda
- Detección de defectos
- Recomendaciones de inventario
- Análisis inteligente de datos
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import numpy as np

from app.db.database import get_db
from app.schemas.prediccion import (
    RespuestaPredictorDemanda,
    RespuestaDetectorDefectos,
    PuntoReorden,
    CantidadEconomicaOrden,
    InsightDashboard,
    AnaliseDatos,
    DatosHistoricos,
    RegistroDefectos
)
from app.core.ml_models import (
    predictor_demanda,
    detector_defectos,
    recomendador_inventario
)
from app.models.lote import Lote
from app.models.producto_terminado import ProductoTerminadoStock, ProductoTerminadoMovimiento
from app.models.colilla import Colilla

router = APIRouter(tags=["IA y Predicciones"])


@router.post("/entrenar/demanda", response_model=dict)
async def entrenar_predictor_demanda(db: Session = Depends(get_db)):
    """
    Entrena el modelo de predicción de demanda con datos históricos
    """
    try:
        # Obtener datos históricos de lotes
        lotes = db.query(Lote).all()
        
        datos_historicos = []
        for lote in lotes:
            if lote.created_at and lote.cantidad_total_programada:
                datos_historicos.append({
                    'fecha': lote.created_at.isoformat(),
                    'cantidad': int(lote.cantidad_total_programada)
                })
        
        if not datos_historicos:
            return {
                "estado": "sin_datos",
                "mensaje": "No hay datos históricos suficientes",
                "registros": 0
            }
        
        # Entrenar modelo
        exito = predictor_demanda.entrenar(datos_historicos)
        
        return {
            "estado": "exito" if exito else "error",
            "mensaje": "Modelo entrenado correctamente" if exito else "Datos insuficientes",
            "registros_usados": len(datos_historicos),
            "modelo_entrenado": predictor_demanda.entrenado
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/demanda", response_model=RespuestaPredictorDemanda)
async def predecir_demanda(
    dias: int = 7,
    dias_historicos: int = 30,
    db: Session = Depends(get_db)
):
    """
    Predice la demanda para los próximos N días
    - dias: Número de días a predecir (1-30)
    - dias_historicos: Días de histórico para contextualizar
    """
    try:
        if dias < 1 or dias > 30:
            dias = 7
        if dias_historicos < 7 or dias_historicos > 365:
            dias_historicos = 30
        
        # Obtener datos recientes de lotes
        fecha_inicio = datetime.now() - timedelta(days=dias_historicos)
        lotes_recientes = db.query(Lote).filter(
            Lote.created_at >= fecha_inicio
        ).order_by(Lote.created_at).all()
        
        datos_recientes = []
        for lote in lotes_recientes:
            if lote.created_at and lote.cantidad_total_programada:
                datos_recientes.append({
                    'fecha': lote.created_at.isoformat(),
                    'cantidad': int(lote.cantidad_total_programada)
                })
        
        # Realizar predicción
        resultado = predictor_demanda.predecir(datos_recientes, dias=dias)
        
        return RespuestaPredictorDemanda(**resultado)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/entrenar/defectos", response_model=dict)
async def entrenar_detector_defectos(db: Session = Depends(get_db)):
    """
    Entrena el modelo de detección de defectos
    """
    try:
        # Obtener datos históricos de defectos
        colillas = db.query(Colilla).filter(Colilla.defecto != None).all()
        
        datos_defectos = []
        for colilla in colillas:
            datos_defectos.append({
                'cantidad_defectos': 1 if colilla.defecto else 0,
                'porcentaje_rechazo': 10.0 if colilla.defecto else 0.0,
                'horas_produccion': 8.0
            })
        
        if not datos_defectos or len(datos_defectos) < 20:
            return {
                "estado": "sin_datos",
                "mensaje": "Se necesitan al menos 20 registros de defectos",
                "registros": len(datos_defectos)
            }
        
        exito = detector_defectos.entrenar(datos_defectos)
        
        return {
            "estado": "exito" if exito else "error",
            "mensaje": "Modelo entrenado correctamente" if exito else "Error en entrenamiento",
            "registros_usados": len(datos_defectos),
            "modelo_entrenado": detector_defectos.entrenado
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/defectos/detectar", response_model=RespuestaDetectorDefectos)
async def detectar_anomalias(
    db: Session = Depends(get_db)
):
    """
    Detecta anomalías en registros de defectos
    """
    try:
        # Obtener registros recientes de colillas
        colillas_recientes = db.query(Colilla).order_by(
            Colilla.id.desc()
        ).limit(50).all()
        
        registros = []
        for colilla in colillas_recientes:
            registros.append({
                'cantidad_defectos': 1 if colilla.defecto else 0,
                'porcentaje_rechazo': 10.0 if colilla.defecto else np.random.uniform(0, 5),
                'horas_produccion': 8.0,
                'colilla_id': colilla.id
            })
        
        resultado = detector_defectos.detectar_anomalias(registros)
        
        return RespuestaDetectorDefectos(**resultado)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inventario/punto-reorden", response_model=PuntoReorden)
async def calcular_punto_reorden(
    demanda_promedio: float,
    lead_time_dias: int = 5,
    desviacion_estandar: float = 10.0,
    factor_seguridad: float = 1.65
):
    """
    Calcula el punto de reorden óptimo para un producto
    
    - demanda_promedio: Promedio de unidades demandadas por día
    - lead_time_dias: Días entre orden y recepción
    - desviacion_estandar: Desviación estándar de la demanda
    - factor_seguridad: Factor Z (default 1.65 = 95% confianza)
    """
    try:
        resultado = recomendador_inventario.calcular_punto_reorden(
            demanda_promedio=demanda_promedio,
            lead_time_dias=lead_time_dias,
            desviacion_estandar=desviacion_estandar,
            factor_seguridad=factor_seguridad
        )
        
        return PuntoReorden(**resultado)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inventario/cantidad-economica", response_model=CantidadEconomicaOrden)
async def calcular_cantidad_economica(
    demanda_anual: float,
    costo_orden: float = 50.0,
    costo_mantenimiento: float = 5.0
):
    """
    Calcula la cantidad económica de orden (EOQ)
    
    - demanda_anual: Cantidad total demandada anualmente
    - costo_orden: Costo fijo por orden
    - costo_mantenimiento: Costo de mantener una unidad por año
    """
    try:
        resultado = recomendador_inventario.recomendar_cantidad_orden(
            demanda_anual=demanda_anual,
            costo_orden=costo_orden,
            costo_mantenimiento=costo_mantenimiento
        )
        
        return CantidadEconomicaOrden(**resultado)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/insights", response_model=AnaliseDatos)
async def obtener_insights(db: Session = Depends(get_db)):
    """
    Genera análisis inteligente para el dashboard
    Incluye:
    - Predicciones de demanda
    - Detección de anomalías
    - Recomendaciones de inventario
    """
    try:
        insights = []
        
        # 1. Predicción de demanda
        fecha_inicio = datetime.now() - timedelta(days=30)
        lotes_recientes = db.query(Lote).filter(
            Lote.created_at >= fecha_inicio
        ).all()
        
        datos_recientes = [
            {
                'fecha': lote.created_at.isoformat(),
                'cantidad': int(lote.cantidad_total_programada or 0)
            }
            for lote in lotes_recientes
            if lote.created_at and lote.cantidad_total_programada
        ]
        
        predicciones = predictor_demanda.predecir(datos_recientes, dias=7)
        
        if predicciones['predicciones']:
            promedio_predicho = np.mean([
                p['cantidad_predicha'] for p in predicciones['predicciones']
            ])
            insights.append(InsightDashboard(
                titulo="Demanda Proyectada",
                descripcion="Predicción de demanda para los próximos 7 días",
                valor_principal=promedio_predicho,
                unidad="unidades/día",
                tipo_alerta="info",
                recomendacion="Ajusta producción según proyecciones"
            ))
        
        # 2. Detección de anomalías
        colillas = db.query(Colilla).order_by(Colilla.id.desc()).limit(20).all()
        registros = [
            {
                'cantidad_defectos': 1 if c.defecto else 0,
                'porcentaje_rechazo': 10.0 if c.defecto else 0.0,
                'horas_produccion': 8.0
            }
            for c in colillas
        ]
        
        anomalias = detector_defectos.detectar_anomalias(registros)
        
        if anomalias['anomalias_detectadas'] > 0:
            insights.append(InsightDashboard(
                titulo="Alerta de Defectos",
                descripcion=f"Se detectaron {anomalias['anomalias_detectadas']} anomalías",
                valor_principal=anomalias['anomalias_detectadas'],
                unidad="anomalías",
                tipo_alerta="warning",
                recomendacion="Revisar lotes con anomalías detectadas"
            ))
        else:
            insights.append(InsightDashboard(
                titulo="Control de Calidad",
                descripcion="Sistema operando dentro de parámetros normales",
                valor_principal=100,
                unidad="%",
                tipo_alerta="success",
                recomendacion="Continuar monitoreo regular"
            ))
        
        # 3. Recomendaciones de inventario
        demanda_promedio = np.mean([lote.cantidad for lote in lotes_recientes if lote.cantidad]) if lotes_recientes else 100
        reorden = recomendador_inventario.calcular_punto_reorden(
            demanda_promedio=demanda_promedio,
            lead_time_dias=5,
            desviacion_estandar=10.0
        )
        
        insights.append(InsightDashboard(
            titulo="Reorden de Inventario",
            descripcion="Punto de reorden recomendado",
            valor_principal=reorden['punto_reorden'],
            unidad="unidades",
            tipo_alerta="info",
            recomendacion=reorden['recomendacion']
        ))
        
        return AnaliseDatos(
            fecha_analisis=datetime.now(),
            predicciones_demanda=RespuestaPredictorDemanda(**predicciones),
            anomalias_calidad=RespuestaDetectorDefectos(**anomalias),
            recomendaciones_inventario=reorden,
            insights=insights
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
