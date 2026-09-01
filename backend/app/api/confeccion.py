from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models import AvanceProduccion, FallaConfeccion, Lote, LoteDetalle, Remision, RemisionDetalle
from app.models.produccion import TipoFalla, EstadoFalla
from app.schemas.produccion import (
    AvanceProduccionCreate, AvanceProduccionUpdate, AvanceProduccionResponse,
    FallaConfeccionCreate, FallaConfeccionUpdate, FallaConfeccionResponse
)

router = APIRouter()

# ========== AVANCES DE PRODUCCIÓN ==========
@router.get("/avances", response_model=List[AvanceProduccionResponse])
def listar_avances(
    skip: int = 0,
    limit: int = 100,
    lote_id: Optional[int] = None,
    taller_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(AvanceProduccion)
    if lote_id:
        query = query.filter(AvanceProduccion.lote_id == lote_id)
    if taller_id:
        query = query.filter(AvanceProduccion.taller_id == taller_id)
    return query.order_by(AvanceProduccion.fecha_avance.desc()).offset(skip).limit(limit).all()

@router.post("/avances", response_model=AvanceProduccionResponse, status_code=status.HTTP_201_CREATED)
def crear_avance(avance: AvanceProduccionCreate, db: Session = Depends(get_db)):
    # Verificar que el lote existe
    lote = db.query(Lote).filter(Lote.id == avance.lote_id).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    
    # Crear el avance
    db_avance = AvanceProduccion(**avance.model_dump())
    db.add(db_avance)
    db.flush()
    
    # Actualizar cantidades en el lote si hay remisión
    if avance.remision_id:
        remision = db.query(Remision).filter(Remision.id == avance.remision_id).first()
        if remision:
            # Actualizar cantidad_confeccionada en los detalles del lote
            # Esto es una simplificación - en producción se debería calcular correctamente
            for detalle_lote in lote.detalles:
                detalle_lote.cantidad_confeccionada = min(
                    detalle_lote.cantidad_confeccionada + avance.cantidad_avance,
                    detalle_lote.cantidad
                )
    
    # Actualizar estado del lote si está completo
    from app.models.lote import EstadoLote
    total_cantidad = sum(d.cantidad for d in lote.detalles)
    total_confeccionada = sum(d.cantidad_confeccionada for d in lote.detalles)
    if total_confeccionada >= total_cantidad:
        lote.estado = EstadoLote.COMPLETADO
    elif total_confeccionada > 0:
        lote.estado = EstadoLote.PARCIALMENTE_ENTREGADO
    
    db.commit()
    db.refresh(db_avance)
    return db_avance

@router.get("/avances/{avance_id}", response_model=AvanceProduccionResponse)
def obtener_avance(avance_id: int, db: Session = Depends(get_db)):
    avance = db.query(AvanceProduccion).filter(AvanceProduccion.id == avance_id).first()
    if not avance:
        raise HTTPException(status_code=404, detail="Avance no encontrado")
    return avance

@router.put("/avances/{avance_id}", response_model=AvanceProduccionResponse)
def actualizar_avance(avance_id: int, avance: AvanceProduccionUpdate, db: Session = Depends(get_db)):
    db_avance = db.query(AvanceProduccion).filter(AvanceProduccion.id == avance_id).first()
    if not db_avance:
        raise HTTPException(status_code=404, detail="Avance no encontrado")
    
    update_data = avance.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_avance, field, value)
    
    db.commit()
    db.refresh(db_avance)
    return db_avance

# ========== FALLAS DE CONFECCIÓN ==========
@router.get("/fallas", response_model=List[FallaConfeccionResponse])
def listar_fallas(
    skip: int = 0,
    limit: int = 100,
    lote_id: Optional[int] = None,
    taller_id: Optional[int] = None,
    estado: Optional[EstadoFalla] = None,
    db: Session = Depends(get_db)
):
    query = db.query(FallaConfeccion)
    if lote_id:
        query = query.filter(FallaConfeccion.lote_id == lote_id)
    if taller_id:
        query = query.filter(FallaConfeccion.taller_id == taller_id)
    if estado:
        query = query.filter(FallaConfeccion.estado == estado)
    return query.order_by(FallaConfeccion.fecha_reporte.desc()).offset(skip).limit(limit).all()

@router.post("/fallas", response_model=FallaConfeccionResponse, status_code=status.HTTP_201_CREATED)
def crear_falla(falla: FallaConfeccionCreate, db: Session = Depends(get_db)):
    # Verificar que el lote existe
    lote = db.query(Lote).filter(Lote.id == falla.lote_id).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    
    db_falla = FallaConfeccion(**falla.model_dump())
    db.add(db_falla)
    db.commit()
    db.refresh(db_falla)
    return db_falla

@router.get("/fallas/{falla_id}", response_model=FallaConfeccionResponse)
def obtener_falla(falla_id: int, db: Session = Depends(get_db)):
    falla = db.query(FallaConfeccion).filter(FallaConfeccion.id == falla_id).first()
    if not falla:
        raise HTTPException(status_code=404, detail="Falla no encontrada")
    return falla

@router.put("/fallas/{falla_id}", response_model=FallaConfeccionResponse)
def actualizar_falla(falla_id: int, falla: FallaConfeccionUpdate, db: Session = Depends(get_db)):
    db_falla = db.query(FallaConfeccion).filter(FallaConfeccion.id == falla_id).first()
    if not db_falla:
        raise HTTPException(status_code=404, detail="Falla no encontrada")
    
    update_data = falla.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_falla, field, value)
    
    # Si se marca como corregida, actualizar fecha de resolución
    if update_data.get("estado") == EstadoFalla.CORREGIDA and not db_falla.fecha_resolucion:
        from datetime import datetime
        db_falla.fecha_resolucion = datetime.now()
    
    db.commit()
    db.refresh(db_falla)
    return db_falla

