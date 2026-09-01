from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Dict, Any, List, Optional
from decimal import Decimal
from app.db.database import get_db
from app.models import (
    Lote, LoteDetalle, Taller, Remision, AvanceProduccion, FallaConfeccion,
    Colilla, RolloStock, OrdenCorte, NOC, Referencia, Color, Talla, FinancieroRegistro
)
from app.models.lote import EstadoLote
from app.models.produccion import ControlCalidad, RegistroProduccion, InspeccionCalidad
from app.models.documentos import TipoMovimientoFinanciero
from app.schemas.dashboard import (
    CostoPrendaResponse,
    RentabilidadLoteResponse,
    ProduccionDiaLineaResponse,
    IndicadoresResponse,
    EficienciaOperarioResponse,
)

router = APIRouter()

@router.get("/estadisticas")
def obtener_estadisticas(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Obtiene estadísticas generales del sistema"""
    
    # Contar lotes por estado
    lotes_por_estado = db.query(
        Lote.estado,
        func.count(Lote.id).label("cantidad")
    ).group_by(Lote.estado).all()
    
    estados_dict = {estado.value: 0 for estado in EstadoLote}
    for estado, cantidad in lotes_por_estado:
        estados_dict[estado.value] = cantidad
    
    # Total de prendas
    total_prendas = db.query(func.sum(LoteDetalle.cantidad)).scalar() or 0
    prendas_en_corte = db.query(func.sum(LoteDetalle.cantidad_cortada)).scalar() or 0
    prendas_en_taller = db.query(func.sum(LoteDetalle.cantidad_en_taller)).scalar() or 0
    prendas_confeccionadas = db.query(func.sum(LoteDetalle.cantidad_confeccionada)).scalar() or 0
    prendas_entregadas = db.query(func.sum(LoteDetalle.cantidad_entregada)).scalar() or 0
    
    # Talleres activos
    talleres_activos = db.query(func.count(Taller.id)).filter(Taller.activo == True).scalar() or 0
    
    # Remisiones pendientes
    remisiones_pendientes = db.query(func.count(Remision.id)).filter(
        Remision.estado.in_(["pendiente", "en_transito"])
    ).scalar() or 0
    
    # Fallas pendientes
    fallas_pendientes = db.query(func.count(FallaConfeccion.id)).filter(
        FallaConfeccion.estado.in_(["reportada", "en_revision"])
    ).scalar() or 0
    
    # Pedidos especiales
    pedidos_especiales = db.query(func.count(Lote.id)).filter(
        Lote.es_pedido_especial == True
    ).scalar() or 0
    
    return {
        "lotes_por_estado": estados_dict,
        "prendas": {
            "total": int(total_prendas),
            "en_corte": int(prendas_en_corte),
            "en_taller": int(prendas_en_taller),
            "confeccionadas": int(prendas_confeccionadas),
            "entregadas": int(prendas_entregadas)
        },
        "talleres_activos": talleres_activos,
        "remisiones_pendientes": remisiones_pendientes,
        "fallas_pendientes": fallas_pendientes,
        "pedidos_especiales": pedidos_especiales
    }

@router.get("/rendimiento-talleres")
def obtener_rendimiento_talleres(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Obtiene el rendimiento de cada taller"""
    
    talleres = db.query(Taller).filter(Taller.activo == True).all()
    
    rendimiento = []
    for taller in talleres:
        # Contar remisiones del taller
        remisiones = db.query(func.count(Remision.id)).filter(
            Remision.taller_id == taller.id
        ).scalar() or 0
        
        # Contar avances del taller
        avances = db.query(func.count(AvanceProduccion.id)).filter(
            AvanceProduccion.taller_id == taller.id
        ).scalar() or 0
        
        # Contar fallas del taller
        fallas = db.query(func.count(FallaConfeccion.id)).filter(
            FallaConfeccion.taller_id == taller.id
        ).scalar() or 0
        
        # Calcular cantidad total confeccionada (simplificado)
        cantidad_confeccionada = db.query(
            func.sum(AvanceProduccion.cantidad_avance)
        ).filter(AvanceProduccion.taller_id == taller.id).scalar() or 0
        
        rendimiento.append({
            "taller_id": taller.id,
            "taller_nombre": taller.nombre,
            "remisiones": remisiones,
            "avances": avances,
            "fallas": fallas,
            "cantidad_confeccionada": int(cantidad_confeccionada),
            "capacidad_diaria": taller.capacidad_diaria
        })
    
    return {"talleres": rendimiento}

@router.get("/lotes-prioridad")
def obtener_lotes_prioridad(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Obtiene lotes con prioridad alta o urgente"""
    
    lotes_prioridad = db.query(Lote).filter(
        Lote.prioridad > 0
    ).order_by(Lote.prioridad.desc(), Lote.created_at.desc()).limit(20).all()
    
    return {
        "lotes": [
            {
                "id": lote.id,
                "numero_lote": lote.numero_lote,
                "prioridad": lote.prioridad,
                "estado": lote.estado.value,
                "es_pedido_especial": lote.es_pedido_especial,
                "fecha_corte": lote.fecha_corte.isoformat() if lote.fecha_corte else None
            }
            for lote in lotes_prioridad
        ]
    }


@router.get("/avance-talleres")
def obtener_avance_talleres(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Obtiene el avance de cada taller basado en colillas asignadas."""
    talleres = db.query(Taller).filter(Taller.activo == True).all()
    resultado = []

    for taller in talleres:
        total_asignado = db.query(func.coalesce(func.sum(Colilla.cantidad_prendas), 0)).filter(
            Colilla.taller_id == taller.id,
            Colilla.activa == True
        ).scalar() or 0

        total_completado = db.query(func.coalesce(func.sum(Colilla.cantidad_completada), 0)).filter(
            Colilla.taller_id == taller.id,
            Colilla.activa == True
        ).scalar() or 0

        porcentaje_avance = 0.0
        if total_asignado:
            porcentaje_avance = round((total_completado / total_asignado) * 100, 2)

        resultado.append({
            "taller": taller.nombre,
            "total_asignado": int(total_asignado),
            "total_completado": int(total_completado),
            "porcentaje_avance": porcentaje_avance
        })

    return resultado


@router.get("/avance-referencias")
def obtener_avance_referencias(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Obtiene el avance de cada referencia basada en cantidades programadas y completadas."""
    detalles = (
        db.query(
            Referencia.nombre.label("referencia"),
            func.coalesce(func.sum(LoteDetalle.cantidad), 0).label("total_programado"),
            func.coalesce(func.sum(LoteDetalle.cantidad_confeccionada), 0).label("total_completado")
        )
        .join(Lote, Lote.id == LoteDetalle.lote_id)
        .join(Referencia, Referencia.id == Lote.referencia_id)
        .group_by(Referencia.nombre)
        .all()
    )

    resultado = []
    for detalle in detalles:
        porcentaje_avance = 0.0
        if detalle.total_programado:
            porcentaje_avance = round((detalle.total_completado / detalle.total_programado) * 100, 2)

        resultado.append({
            "referencia": detalle.referencia,
            "total_programado": int(detalle.total_programado),
            "total_completado": int(detalle.total_completado),
            "porcentaje_avance": porcentaje_avance
        })

    return resultado


@router.get("/resumen-negocio")
def resumen_negocio_textil(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    KPIs de alto nivel para el tablero tipo confección textil
    (inventario tela, órdenes de corte, lotes, calidad, documentos).
    """
    total_metros_tela = db.query(func.coalesce(func.sum(RolloStock.cantidad_actual), 0)).scalar() or 0
    lineas_stock = db.query(func.count(RolloStock.id)).scalar() or 0

    ordenes_corte = db.query(func.count(OrdenCorte.id)).scalar() or 0

    estados_activos = (
        EstadoLote.EN_CORTE,
        EstadoLote.CORTE_COMPLETADO,
        EstadoLote.EN_CAMINO,
        EstadoLote.EN_TALLER,
        EstadoLote.EN_CONFECCION,
        EstadoLote.PARCIALMENTE_ENTREGADO,
    )
    lotes_activos = (
        db.query(func.count(Lote.id)).filter(Lote.estado.in_(estados_activos)).scalar() or 0
    )

    inspecciones_hoy = db.query(func.count(ControlCalidad.id)).scalar() or 0
    nocs = db.query(func.count(NOC.id)).scalar() or 0

    return {
        "inventario_tela": {
            "lineas_stock": int(lineas_stock),
            "metros_totales": float(total_metros_tela),
        },
        "corte": {"ordenes_registradas": int(ordenes_corte)},
        "lotes": {"activos": int(lotes_activos)},
        "calidad": {"inspecciones_registradas": int(inspecciones_hoy)},
        "documentacion": {"nocs_generados": int(nocs)},
    }


@router.get("/detalle-colores-tallas")
def obtener_detalle_colores_tallas(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Obtiene detalle de colores y tallas por referencia"""
    
    # Query para obtener detalle de lotes con colores y tallas
    detalles = (
        db.query(
            Referencia.nombre.label("referencia"),
            LoteDetalle.color_nombre.label("color"),
            Talla.nombre.label("talla"),
            LoteDetalle.cantidad,
            LoteDetalle.cantidad_confeccionada
        )
        .join(Lote, Lote.referencia_id == Referencia.id)
        .join(LoteDetalle, LoteDetalle.lote_id == Lote.id)
        .join(Talla, Talla.id == LoteDetalle.talla_id)
        .filter(Lote.estado != EstadoLote.CANCELADO)
        .all()
    )
    
    result = []
    for detalle in detalles:
        faltante = detalle.cantidad - (detalle.cantidad_confeccionada or 0)
        result.append({
            "referencia": detalle.referencia,
            "color": detalle.color,
            "talla": detalle.talla,
            "programado": detalle.cantidad,
            "completado": detalle.cantidad_confeccionada or 0,
            "faltante": faltante
        })
    
    return result


def _sum_financiero_categorias(registros):
    costo_tela = Decimal("0")
    costo_mano_obra = Decimal("0")
    costo_insumos = Decimal("0")
    costo_otros = Decimal("0")

    for registro in registros:
        descripcion = (registro.descripcion or "").lower()
        monto = registro.monto or Decimal("0")
        if "tela" in descripcion:
            costo_tela += monto
        elif "mano" in descripcion or "obra" in descripcion:
            costo_mano_obra += monto
        elif "insumo" in descripcion:
            costo_insumos += monto
        else:
            costo_otros += monto

    return costo_tela, costo_mano_obra, costo_insumos, costo_otros


@router.get("/costo-prenda", response_model=CostoPrendaResponse)
def obtener_costo_prenda(
    noc_id: Optional[int] = None,
    lote_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    if noc_id is None and lote_id is None:
        raise HTTPException(status_code=400, detail="Se debe especificar noc_id o lote_id")

    if noc_id is not None:
        noc = db.query(NOC).filter(NOC.id == noc_id).first()
        if not noc:
            raise HTTPException(status_code=404, detail="NOC no encontrada")
        lote_id = noc.lote_id

    lote = db.query(Lote).filter(Lote.id == lote_id).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")

    total_prendas = db.query(func.coalesce(func.sum(LoteDetalle.cantidad), 0)).filter(LoteDetalle.lote_id == lote_id).scalar() or 0
    registros = (
        db.query(FinancieroRegistro)
        .join(NOC, FinancieroRegistro.noc_id == NOC.id)
        .filter(NOC.lote_id == lote_id, FinancieroRegistro.tipo == TipoMovimientoFinanciero.COSTO_PROCESO)
        .all()
    )

    costo_tela, costo_mano_obra, costo_insumos, costo_otros = _sum_financiero_categorias(registros)
    costo_total = costo_tela + costo_mano_obra + costo_insumos + costo_otros
    costo_unitario = (costo_total / Decimal(total_prendas)) if total_prendas > 0 else Decimal("0")

    return CostoPrendaResponse(
        noc_id=noc_id,
        lote_id=lote_id,
        total_prendas=int(total_prendas),
        costo_tela=costo_tela,
        costo_mano_obra=costo_mano_obra,
        costo_insumos=costo_insumos,
        costo_otros=costo_otros,
        costo_total=costo_total,
        costo_unitario=costo_unitario,
    )


@router.get("/rentabilidad-lote", response_model=RentabilidadLoteResponse)
def obtener_rentabilidad_lote(
    lote_id: int,
    db: Session = Depends(get_db),
):
    lote = db.query(Lote).filter(Lote.id == lote_id).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")

    total_prendas = db.query(func.coalesce(func.sum(LoteDetalle.cantidad), 0)).filter(LoteDetalle.lote_id == lote_id).scalar() or 0
    registros = (
        db.query(FinancieroRegistro)
        .join(NOC, FinancieroRegistro.noc_id == NOC.id)
        .filter(NOC.lote_id == lote_id)
        .all()
    )

    anticipo_total = sum((registro.monto for registro in registros if registro.tipo == TipoMovimientoFinanciero.ANTICIPO), Decimal("0"))
    costos = [registro for registro in registros if registro.tipo == TipoMovimientoFinanciero.COSTO_PROCESO]
    costo_tela, costo_mano_obra, costo_insumos, costo_otros = _sum_financiero_categorias(costos)
    costo_total = costo_tela + costo_mano_obra + costo_insumos + costo_otros
    rentabilidad = anticipo_total - costo_total
    rentabilidad_pct = (rentabilidad / anticipo_total * Decimal("100")) if anticipo_total > 0 else None
    costo_unitario_promedio = (costo_total / Decimal(total_prendas)) if total_prendas > 0 else Decimal("0")

    return RentabilidadLoteResponse(
        lote_id=lote_id,
        total_prendas=int(total_prendas),
        anticipo_total=anticipo_total,
        costo_total=costo_total,
        rentabilidad=rentabilidad,
        rentabilidad_pct=rentabilidad_pct,
        costo_unitario_promedio=costo_unitario_promedio,
    )


@router.get("/produccion-dia-linea", response_model=List[ProduccionDiaLineaResponse])
@router.get("/tiempos-produccion", response_model=List[ProduccionDiaLineaResponse])
def obtener_produccion_dia_linea(db: Session = Depends(get_db)):
    registros = (
        db.query(
            func.date(RegistroProduccion.tiempo_inicio).label("fecha"),
            RegistroProduccion.linea_produccion,
            func.coalesce(func.sum(RegistroProduccion.cantidad_producida), 0).label("cantidad_producida"),
            func.coalesce(func.sum(RegistroProduccion.cantidad_rechazada), 0).label("cantidad_rechazada"),
            func.coalesce(func.sum(RegistroProduccion.tiempo_total_minutos), 0).label("tiempo_total_minutos"),
        )
        .group_by(func.date(RegistroProduccion.tiempo_inicio), RegistroProduccion.linea_produccion)
        .order_by(func.date(RegistroProduccion.tiempo_inicio).desc())
        .all()
    )

    resultado = []
    for registro in registros:
        horas = float(registro.tiempo_total_minutos or 0) / 60.0
        eficiencia = float(registro.cantidad_producida) / horas if horas > 0 else 0.0
        resultado.append(ProduccionDiaLineaResponse(
            fecha=registro.fecha,
            linea_produccion=registro.linea_produccion,
            cantidad_producida=int(registro.cantidad_producida),
            cantidad_rechazada=int(registro.cantidad_rechazada),
            eficiencia_hph=round(eficiencia, 2),
        ))

    return resultado


@router.get("/indicadores", response_model=IndicadoresResponse)
def obtener_indicadores(db: Session = Depends(get_db)):
    total_metros_tizado = db.query(func.coalesce(func.sum(OrdenCorte.metros_tizado), 0)).scalar() or 0
    total_metros_desperdicio = db.query(func.coalesce(func.sum(OrdenCorte.metros_desperdicio), 0)).scalar() or 0
    desperdicio_tela_pct = float(total_metros_desperdicio) / float(total_metros_tizado) * 100 if total_metros_tizado > 0 else 0.0

    total_inspeccionada = db.query(func.coalesce(func.sum(InspeccionCalidad.cantidad_inspeccionada), 0)).scalar() or 0
    total_defectuosa = db.query(func.coalesce(func.sum(InspeccionCalidad.cantidad_defectuosa), 0)).scalar() or 0
    defectos_pct = float(total_defectuosa) / float(total_inspeccionada) * 100 if total_inspeccionada > 0 else 0.0

    total_prendas = (
        db.query(func.coalesce(func.sum(LoteDetalle.cantidad), 0))
        .scalar() or 0
    )
    costo_total = (
        db.query(func.coalesce(func.sum(FinancieroRegistro.monto), 0))
        .join(NOC, FinancieroRegistro.noc_id == NOC.id)
        .filter(FinancieroRegistro.tipo == TipoMovimientoFinanciero.COSTO_PROCESO)
        .scalar() or Decimal("0")
    )
    costo_unitario_promedio = (Decimal(costo_total) / Decimal(total_prendas)) if total_prendas > 0 else Decimal("0")

    registros_operario = (
        db.query(
            RegistroProduccion.operario,
            func.coalesce(func.sum(RegistroProduccion.cantidad_producida), 0).label("produccion_total"),
            func.coalesce(func.sum(RegistroProduccion.tiempo_total_minutos), 0).label("tiempo_total_minutos"),
        )
        .filter(RegistroProduccion.operario.isnot(None), RegistroProduccion.tiempo_total_minutos.isnot(None))
        .group_by(RegistroProduccion.operario)
        .order_by(func.sum(RegistroProduccion.cantidad_producida).desc())
        .all()
    )

    eficiencia_operarios = []
    for registro in registros_operario:
        horas = float(registro.tiempo_total_minutos or 0) / 60.0
        piezas_por_hora = float(registro.produccion_total) / horas if horas > 0 else 0.0
        eficiencia_operarios.append(EficienciaOperarioResponse(
            operario=registro.operario,
            produccion_total=int(registro.produccion_total),
            horas_trabajadas=round(horas, 2),
            piezas_por_hora=round(piezas_por_hora, 2),
        ))

    return IndicadoresResponse(
        desperdicio_tela_pct=round(desperdicio_tela_pct, 2),
        defectos_pct=round(defectos_pct, 2),
        costo_unitario_promedio=float(round(costo_unitario_promedio, 2)),
        eficiencia_operarios=eficiencia_operarios,
    )


@router.get("/avance-referencias")
def obtener_avance_referencias(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Obtiene avance de producción por referencia"""
    referencias = db.query(Referencia).all()
    
    result = []
    for ref in referencias:
        total_programado = db.query(func.sum(LoteDetalle.cantidad)).join(
            Lote, Lote.id == LoteDetalle.lote_id
        ).filter(Lote.referencia_id == ref.id).scalar() or 0
        
        total_completado = db.query(func.sum(LoteDetalle.cantidad_confeccionada)).join(
            Lote, Lote.id == LoteDetalle.lote_id
        ).filter(Lote.referencia_id == ref.id).scalar() or 0
        
        porcentaje = (total_completado / total_programado * 100) if total_programado > 0 else 0
        
        result.append({
            "referencia": ref.nombre,
            "total_programado": total_programado,
            "total_completado": total_completado,
            "porcentaje_avance": round(porcentaje, 2)
        })
    
    return result


@router.get("/avance-talleres")
def obtener_avance_talleres(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Obtiene avance de producción por taller"""
    talleres = db.query(Taller).filter(Taller.activo == True).all()
    
    result = []
    for taller in talleres:
        # Contar remisiones (trabajo asignado al taller)
        total_asignado = db.query(func.count(Remision.id)).filter(
            Remision.taller_id == taller.id
        ).scalar() or 0
        
        # Contar remisiones completadas
        total_completado = db.query(func.count(Remision.id)).filter(
            Remision.taller_id == taller.id,
            Remision.estado == "completada"
        ).scalar() or 0
        
        porcentaje = (total_completado / total_asignado * 100) if total_asignado > 0 else 0
        
        result.append({
            "taller": taller.nombre,
            "total_asignado": total_asignado,
            "total_completado": total_completado,
            "porcentaje_avance": round(porcentaje, 2)
        })
    
    return result


@router.get("/tiempos-produccion")
def obtener_tiempos_produccion(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Obtiene comparativa de tiempos estimados vs reales de producción"""
    lotes = db.query(Lote).filter(
        Lote.estado.in_([EstadoLote.COMPLETADO, EstadoLote.PARCIALMENTE_ENTREGADO])
    ).all()
    
    result = []
    for lote in lotes:
        if not lote.referencia or not lote.fecha_corte or not lote.fecha_asignacion:
            continue
        
        # Calcular tiempo estimado (basado en la capacidad del taller)
        tiempo_estimado = 5  # días por defecto
        if lote.detalles:
            total_prendas = sum(d.cantidad for d in lote.detalles)
            # Asumiendo 100 prendas/día como baseline
            tiempo_estimado = max(1, total_prendas / 100)
        
        # Tiempo real
        if lote.fecha_completacion:
            tiempo_real = (lote.fecha_completacion - lote.fecha_asignacion).days
        else:
            tiempo_real = (func.now() - lote.fecha_asignacion).days
        
        diferencia = tiempo_real - tiempo_estimado
        
        result.append({
            "referencia": lote.referencia.nombre,
            "tiempo_estimado_dias": round(tiempo_estimado, 1),
            "tiempo_real_dias": tiempo_real,
            "diferencia_dias": round(diferencia, 1)
        })
    
    return result

