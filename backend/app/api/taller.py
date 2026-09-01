from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models import Taller, Remision, RemisionDetalle, Lote
from app.models.taller import EstadoRemision
from app.schemas.taller import (
    TallerCreate, TallerUpdate, TallerResponse,
    RemisionCreate, RemisionUpdate, RemisionResponse
)
from app.core.notifications import send_notification_to_taller
from app.core.business_rules import validar_stock_disponible_remision

router = APIRouter()

# ========== TALLERES ==========
@router.get("/", response_model=List[TallerResponse])
def listar_talleres(skip: int = 0, limit: int = 100, activo: bool = None, db: Session = Depends(get_db)):
    query = db.query(Taller)
    if activo is not None:
        query = query.filter(Taller.activo == activo)
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=TallerResponse, status_code=status.HTTP_201_CREATED)
def crear_taller(taller: TallerCreate, db: Session = Depends(get_db)):
    if db.query(Taller).filter(Taller.codigo == taller.codigo).first():
        raise HTTPException(status_code=400, detail="El código de taller ya existe")
    db_taller = Taller(**taller.model_dump())
    db.add(db_taller)
    db.commit()
    db.refresh(db_taller)
    return db_taller

# ========== REMISIONES ==========
@router.get("/remisiones", response_model=List[RemisionResponse])
def listar_remisiones(
    skip: int = 0,
    limit: int = 100,
    taller_id: Optional[int] = None,
    estado: Optional[EstadoRemision] = None,
    db: Session = Depends(get_db)
):
    from sqlalchemy.orm import joinedload
    query = db.query(Remision).options(
        joinedload(Remision.taller),
        joinedload(Remision.lote),
        joinedload(Remision.detalles).joinedload(RemisionDetalle.talla)
    )
    if taller_id:
        query = query.filter(Remision.taller_id == taller_id)
    if estado:
        query = query.filter(Remision.estado == estado)
    return query.order_by(Remision.created_at.desc()).offset(skip).limit(limit).all()

@router.post("/remisiones", response_model=RemisionResponse, status_code=status.HTTP_201_CREATED)
def crear_remision(remision: RemisionCreate, db: Session = Depends(get_db)):
    # Verificar que el número de remisión no exista
    if db.query(Remision).filter(Remision.numero_remision == remision.numero_remision).first():
        raise HTTPException(status_code=400, detail="El número de remisión ya existe")
    
    # Verificar que el lote existe
    lote = db.query(Lote).filter(Lote.id == remision.lote_id).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    
    # Verificar que el taller existe
    taller = db.query(Taller).filter(Taller.id == remision.taller_id).first()
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")
    
# Crear la remisión
    remision_data = remision.model_dump(exclude={"detalles"})
    db_remision = Remision(**remision_data)
    db.add(db_remision)
    db.flush()
    
    # Crear los detalles de la remisión
    for detalle in remision.detalles:
        db_detalle = RemisionDetalle(remision_id=db_remision.id, **detalle.model_dump())
        db.add(db_detalle)
    
    db.flush()
    
    # RN-2: Validar stock disponible si la remisión se crea en estado en tránsito
    if remision.estado == EstadoRemision.EN_TRANSITO:
        validar_stock_disponible_remision(db, db_remision.id)

    # Actualizar estado del lote
    from app.models.lote import EstadoLote
    lote.estado = EstadoLote.EN_CAMINO
    lote.fecha_asignacion = remision.fecha_remision
    
    db.commit()
    db.refresh(db_remision)

    # Enviar notificación al taller con la orden asignada
    try:
        from sqlalchemy.orm import joinedload
        # Recargar remisión con todas las relaciones necesarias para la notificación
        remision_completa = db.query(Remision).options(
            joinedload(Remision.taller),
            joinedload(Remision.lote).joinedload(Lote.referencia),
            joinedload(Remision.lote).joinedload(Lote.material),
            joinedload(Remision.detalles).joinedload(RemisionDetalle.talla)
        ).filter(Remision.id == db_remision.id).first()
        
        if remision_completa:
            send_notification_to_taller(remision_completa.taller, remision_completa, remision_completa.detalles)
    except Exception as e:
        # No bloquear la creación por fallas en notificación, pero loguear el error
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Error enviando notificación: {e}")
    
    return db_remision


@router.post("/remisiones/bulk", response_model=List[RemisionResponse], status_code=status.HTTP_201_CREATED)
def crear_remisiones_bulk(remisiones: List[RemisionCreate], db: Session = Depends(get_db)):
    """Crear múltiples remisiones en un solo request (asignar varias referencias a talleres)."""
    created = []
    # Validar colisiones de numero_remision en DB
    numeros = [r.numero_remision for r in remisiones]
    exist = db.query(Remision).filter(Remision.numero_remision.in_(numeros)).all()
    if exist:
        existentes = [e.numero_remision for e in exist]
        raise HTTPException(status_code=400, detail=f"Los siguientes números de remisión ya existen: {existentes}")

    for rem in remisiones:
        # Verificar lote
        lote = db.query(Lote).filter(Lote.id == rem.lote_id).first()
        if not lote:
            raise HTTPException(status_code=404, detail=f"Lote no encontrado: {rem.lote_id}")

        # Verificar taller
        taller = db.query(Taller).filter(Taller.id == rem.taller_id).first()
        if not taller:
            raise HTTPException(status_code=404, detail=f"Taller no encontrado: {rem.taller_id}")

        rem_data = rem.model_dump(exclude={"detalles"})
        db_rem = Remision(**rem_data)
        db.add(db_rem)
        db.flush()

        for detalle in rem.detalles:
            db_detalle = RemisionDetalle(remision_id=db_rem.id, **detalle.model_dump())
            db.add(db_detalle)

        # Actualizar estado del lote
        from app.models.lote import EstadoLote
        lote.estado = EstadoLote.EN_CAMINO
        lote.fecha_asignacion = rem.fecha_remision

        created.append(db_rem)

    db.commit()

    # Refrescar objetos y enviar notificaciones
    from sqlalchemy.orm import joinedload
    for db_rem in created:
        db.refresh(db_rem)
        try:
            # Recargar remisión con todas las relaciones necesarias
            remision_completa = db.query(Remision).options(
                joinedload(Remision.taller),
                joinedload(Remision.lote).joinedload(Lote.referencia),
                joinedload(Remision.lote).joinedload(Lote.material),
                joinedload(Remision.detalles).joinedload(RemisionDetalle.talla)
            ).filter(Remision.id == db_rem.id).first()
            
            if remision_completa:
                send_notification_to_taller(remision_completa.taller, remision_completa, remision_completa.detalles)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error enviando notificación para remisión {db_rem.id}: {e}")

    return created

@router.get("/remisiones/{remision_id}", response_model=RemisionResponse)
def obtener_remision(remision_id: int, db: Session = Depends(get_db)):
    remision = db.query(Remision).filter(Remision.id == remision_id).first()
    if not remision:
        raise HTTPException(status_code=404, detail="Remisión no encontrada")
    return remision

@router.put("/remisiones/{remision_id}", response_model=RemisionResponse)
def actualizar_remision(remision_id: int, remision: RemisionUpdate, db: Session = Depends(get_db)):
    db_remision = db.query(Remision).filter(Remision.id == remision_id).first()
    if not db_remision:
        raise HTTPException(status_code=404, detail="Remisión no encontrada")
    
    update_data = remision.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_remision, field, value)
    
    db.commit()
    db.refresh(db_remision)
    return db_remision

@router.patch("/remisiones/{remision_id}/estado", response_model=RemisionResponse)
def actualizar_estado_remision(remision_id: int, estado: dict, db: Session = Depends(get_db)):
    estado_value = estado.get("estado") if isinstance(estado, dict) else estado
    revisado_por = estado.get("revisado_por") if isinstance(estado, dict) else None
    
    if isinstance(estado_value, str):
        estado_value = EstadoRemision(estado_value)
    db_remision = db.query(Remision).filter(Remision.id == remision_id).first()
    if not db_remision:
        raise HTTPException(status_code=404, detail="Remisión no encontrada")
    
    db_remision.estado = estado_value
    if estado_value == EstadoRemision.RECIBIDA:
        from datetime import datetime
        db_remision.fecha_recepcion = datetime.now()
        if revisado_por:
            db_remision.revisado_por = revisado_por
        # Actualizar estado del lote
        from app.models.lote import EstadoLote
        lote = db.query(Lote).filter(Lote.id == db_remision.lote_id).first()
        if lote:
            lote.estado = EstadoLote.EN_TALLER
    
    db.commit()
    db.refresh(db_remision)
    return db_remision

@router.get("/{taller_id}", response_model=TallerResponse)
def obtener_taller(taller_id: int, db: Session = Depends(get_db)):
    taller = db.query(Taller).filter(Taller.id == taller_id).first()
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")
    return taller

@router.put("/{taller_id}", response_model=TallerResponse)
def actualizar_taller(taller_id: int, taller: TallerUpdate, db: Session = Depends(get_db)):
    db_taller = db.query(Taller).filter(Taller.id == taller_id).first()
    if not db_taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")
    update_data = taller.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_taller, field, value)
    db.commit()
    db.refresh(db_taller)
    return db_taller

@router.delete("/{taller_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_taller(taller_id: int, db: Session = Depends(get_db)):
    taller = db.query(Taller).filter(Taller.id == taller_id).first()
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")
    db.delete(taller)
    db.commit()
    return None

