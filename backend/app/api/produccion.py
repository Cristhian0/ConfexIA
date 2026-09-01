from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models import Lote
from app.models.produccion import OrdenProduccion, RegistroProduccion, EstadoOrdenProduccion
from app.schemas.produccion import (
    OrdenProduccionCreate, OrdenProduccionUpdate, OrdenProduccionResponse,
    RegistroProduccionCreate, RegistroProduccionUpdate, RegistroProduccionResponse
)
from app.core.business_rules import validar_cierre_orden_produccion

router = APIRouter()

# ========== RF-11: ÓRDENES DE PRODUCCIÓN ==========
@router.get("/ordenes", response_model=List[OrdenProduccionResponse])
def listar_ordenes_produccion(
    skip: int = 0,
    limit: int = 100,
    lote_id: Optional[int] = None,
    estado: Optional[EstadoOrdenProduccion] = None,
    db: Session = Depends(get_db)
):
    """Listar órdenes de producción con filtros opcionales"""
    query = db.query(OrdenProduccion).options(
        joinedload(OrdenProduccion.registros_produccion)
    )
    
    if lote_id:
        query = query.filter(OrdenProduccion.lote_id == lote_id)
    if estado:
        query = query.filter(OrdenProduccion.estado == estado)
    
    return query.order_by(OrdenProduccion.fecha_creacion.desc()).offset(skip).limit(limit).all()

@router.post("/ordenes", response_model=OrdenProduccionResponse, status_code=status.HTTP_201_CREATED)
def crear_orden_produccion(orden: OrdenProduccionCreate, db: Session = Depends(get_db)):
    """RF-11: Crear orden de confección asociada a un lote"""
    # Verificar que el lote existe
    lote = db.query(Lote).filter(Lote.id == orden.lote_id).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    
    # Generar número de orden
    ultimo_numero = db.query(OrdenProduccion).order_by(OrdenProduccion.id.desc()).first()
    numero_orden = f"OP-{(ultimo_numero.id + 1) if ultimo_numero else 1:06d}"
    
    # Crear la orden
    db_orden = OrdenProduccion(
        numero_orden=numero_orden,
        lote_id=orden.lote_id,
        observaciones=orden.observaciones
    )
    db.add(db_orden)
    db.commit()
    db.refresh(db_orden)
    
    return db_orden

@router.get("/ordenes/{orden_id}", response_model=OrdenProduccionResponse)
def obtener_orden_produccion(orden_id: int, db: Session = Depends(get_db)):
    """Obtener una orden de producción específica"""
    orden = db.query(OrdenProduccion).options(
        joinedload(OrdenProduccion.registros_produccion)
    ).filter(OrdenProduccion.id == orden_id).first()
    
    if not orden:
        raise HTTPException(status_code=404, detail="Orden de producción no encontrada")
    
    return orden

@router.patch("/ordenes/{orden_id}", response_model=OrdenProduccionResponse)
def actualizar_orden_produccion(orden_id: int, update: OrdenProduccionUpdate, db: Session = Depends(get_db)):
    """Actualizar estado o información de una orden de producción
    
    RN-1: Si se intenta cerrar/completar la orden, valida que no haya inspecciones pendientes
    """
    orden = db.query(OrdenProduccion).filter(OrdenProduccion.id == orden_id).first()
    
    if not orden:
        raise HTTPException(status_code=404, detail="Orden de producción no encontrada")
    
    # RN-1: Validar cierre de orden si se intenta cambiar a estado "completada"
    if update.estado == EstadoOrdenProduccion.COMPLETADA:
        validar_cierre_orden_produccion(db, orden_id)
    
    # Actualizar solo los campos proporcionados
    if update.estado is not None:
        orden.estado = update.estado
    if update.fecha_inicio is not None:
        orden.fecha_inicio = update.fecha_inicio
    if update.fecha_fin is not None:
        orden.fecha_fin = update.fecha_fin
    if update.observaciones is not None:
        orden.observaciones = update.observaciones
    
    db.commit()
    db.refresh(orden)
    
    return orden

# ========== RF-12, RF-13, RF-14: REGISTROS DE PRODUCCIÓN ==========
@router.get("/registros", response_model=List[RegistroProduccionResponse])
def listar_registros_produccion(
    skip: int = 0,
    limit: int = 100,
    orden_produccion_id: Optional[int] = None,
    operario: Optional[str] = None,
    linea_produccion: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Listar registros de producción con filtros por operario o línea"""
    query = db.query(RegistroProduccion)
    
    if orden_produccion_id:
        query = query.filter(RegistroProduccion.orden_produccion_id == orden_produccion_id)
    if operario:
        query = query.filter(RegistroProduccion.operario.ilike(f"%{operario}%"))
    if linea_produccion:
        query = query.filter(RegistroProduccion.linea_produccion == linea_produccion)
    
    return query.order_by(RegistroProduccion.tiempo_inicio.desc()).offset(skip).limit(limit).all()

@router.post("/registros", response_model=RegistroProduccionResponse, status_code=status.HTTP_201_CREATED)
def crear_registro_produccion(registro: RegistroProduccionCreate, db: Session = Depends(get_db)):
    """
    RF-12: Registrar producción por operación (Ensamble, Costura, Fileteado, Terminación)
    RF-13: Registrar por operario o línea de producción
    RF-14: Registrar tiempos de inicio y fin
    """
    # Verificar que la orden existe
    orden = db.query(OrdenProduccion).filter(OrdenProduccion.id == registro.orden_produccion_id).first()
    if not orden:
        raise HTTPException(status_code=404, detail="Orden de producción no encontrada")
    
    # Calcular tiempo total si viene tiempo_fin
    tiempo_total_minutos = None
    if registro.tiempo_fin:
        delta = registro.tiempo_fin - registro.tiempo_inicio
        tiempo_total_minutos = int(delta.total_seconds() / 60)
    
    # Crear el registro
    db_registro = RegistroProduccion(
        orden_produccion_id=registro.orden_produccion_id,
        operacion=registro.operacion,
        operario=registro.operario,
        linea_produccion=registro.linea_produccion,
        cantidad_producida=registro.cantidad_producida,
        cantidad_rechazada=registro.cantidad_rechazada,
        tiempo_inicio=registro.tiempo_inicio,
        tiempo_fin=registro.tiempo_fin,
        tiempo_total_minutos=tiempo_total_minutos,
        notas=registro.notas
    )
    
    db.add(db_registro)
    
    # Actualizar estado de la orden si es el primer registro
    if orden.estado == EstadoOrdenProduccion.PENDIENTE:
        orden.estado = EstadoOrdenProduccion.EN_PROGRESO
        orden.fecha_inicio = registro.tiempo_inicio
    
    db.commit()
    db.refresh(db_registro)
    
    return db_registro

@router.get("/registros/{registro_id}", response_model=RegistroProduccionResponse)
def obtener_registro_produccion(registro_id: int, db: Session = Depends(get_db)):
    """Obtener un registro de producción específico"""
    registro = db.query(RegistroProduccion).filter(RegistroProduccion.id == registro_id).first()
    
    if not registro:
        raise HTTPException(status_code=404, detail="Registro de producción no encontrado")
    
    return registro

@router.patch("/registros/{registro_id}", response_model=RegistroProduccionResponse)
def actualizar_registro_produccion(registro_id: int, update: RegistroProduccionUpdate, db: Session = Depends(get_db)):
    """Actualizar un registro de producción (principalmente para completar tiempo_fin)"""
    registro = db.query(RegistroProduccion).filter(RegistroProduccion.id == registro_id).first()
    
    if not registro:
        raise HTTPException(status_code=404, detail="Registro de producción no encontrado")
    
    # Actualizar campos
    if update.operario is not None:
        registro.operario = update.operario
    if update.linea_produccion is not None:
        registro.linea_produccion = update.linea_produccion
    if update.cantidad_producida is not None:
        registro.cantidad_producida = update.cantidad_producida
    if update.cantidad_rechazada is not None:
        registro.cantidad_rechazada = update.cantidad_rechazada
    if update.tiempo_fin is not None:
        registro.tiempo_fin = update.tiempo_fin
        # Recalcular tiempo total
        delta = registro.tiempo_fin - registro.tiempo_inicio
        registro.tiempo_total_minutos = int(delta.total_seconds() / 60)
    if update.notas is not None:
        registro.notas = update.notas
    
    db.commit()
    db.refresh(registro)
    
    return registro

@router.delete("/registros/{registro_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_registro_produccion(registro_id: int, db: Session = Depends(get_db)):
    """Eliminar un registro de producción"""
    registro = db.query(RegistroProduccion).filter(RegistroProduccion.id == registro_id).first()
    
    if not registro:
        raise HTTPException(status_code=404, detail="Registro de producción no encontrado")
    
    db.delete(registro)
    db.commit()
    
    return None

@router.post("/ordenes/{orden_id}/completar", response_model=OrdenProduccionResponse)
def completar_orden_produccion(orden_id: int, db: Session = Depends(get_db)):
    """Marcar una orden de producción como completada"""
    orden = db.query(OrdenProduccion).filter(OrdenProduccion.id == orden_id).first()
    
    if not orden:
        raise HTTPException(status_code=404, detail="Orden de producción no encontrada")
    
    orden.estado = EstadoOrdenProduccion.COMPLETADA
    orden.fecha_fin = datetime.now()
    
    db.commit()
    db.refresh(orden)
    
    return orden
