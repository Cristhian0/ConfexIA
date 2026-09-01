from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models import Lote, Remision
from app.models.produccion import ControlCalidad, ImperfectoCalidad, EstadoControlCalidad
from app.schemas.produccion import (
    ControlCalidadCreate, ControlCalidadUpdate, ControlCalidadResponse,
    ImperfectoCalidadCreate, ImperfectoCalidadUpdate, ImperfectoCalidadResponse
)
from app.core.business_rules import actualizar_inventario_pt_por_calidad

router = APIRouter()

# ========== CONTROL DE CALIDAD ==========
@router.get("/calidad", response_model=List[ControlCalidadResponse])
def listar_controles_calidad(
    skip: int = 0,
    limit: int = 100,
    lote_id: Optional[int] = None,
    remision_id: Optional[int] = None,
    estado: Optional[EstadoControlCalidad] = None,
    db: Session = Depends(get_db)
):
    from sqlalchemy.orm import joinedload
    query = db.query(ControlCalidad).options(
        joinedload(ControlCalidad.lote),
        joinedload(ControlCalidad.remision).joinedload(Remision.taller),
        joinedload(ControlCalidad.imperfectos)
    )
    if lote_id:
        query = query.filter(ControlCalidad.lote_id == lote_id)
    if remision_id:
        query = query.filter(ControlCalidad.remision_id == remision_id)
    if estado:
        query = query.filter(ControlCalidad.estado == estado)
    return query.order_by(ControlCalidad.fecha_inspeccion.desc()).offset(skip).limit(limit).all()

@router.post("/calidad", response_model=ControlCalidadResponse, status_code=status.HTTP_201_CREATED)
def crear_control_calidad(control: ControlCalidadCreate, db: Session = Depends(get_db)):
    # Verificar que el lote existe
    lote = db.query(Lote).filter(Lote.id == control.lote_id).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    
    # Verificar que la remisión existe
    remision = db.query(Remision).filter(Remision.id == control.remision_id).first()
    if not remision:
        raise HTTPException(status_code=404, detail="Remisión no encontrada")
    
    # Crear el control de calidad
    control_data = control.model_dump(exclude={"imperfectos"})
    db_control = ControlCalidad(**control_data)
    db.add(db_control)
    db.flush()
    
    # Crear los imperfectos si existen
    for imperfecto in control.imperfectos:
        db_imperfecto = ImperfectoCalidad(control_calidad_id=db_control.id, **imperfecto.model_dump())
        db.add(db_imperfecto)
    
    # Actualizar estado de la remisión si hay devoluciones
    if control.cantidad_devuelta > 0:
        db_control.estado = EstadoControlCalidad.DEVUELTO_TALLER
        db_control.fecha_devolucion = control.fecha_inspeccion
    
    db.commit()
    db.refresh(db_control)
    
    # Cargar las relaciones para la respuesta
    from sqlalchemy.orm import joinedload
    control_completo = db.query(ControlCalidad).options(
        joinedload(ControlCalidad.lote),
        joinedload(ControlCalidad.remision).joinedload(Remision.taller),
        joinedload(ControlCalidad.imperfectos)
    ).filter(ControlCalidad.id == db_control.id).first()
    
    return control_completo

@router.get("/calidad/{control_id}", response_model=ControlCalidadResponse)
def obtener_control_calidad(control_id: int, db: Session = Depends(get_db)):
    from sqlalchemy.orm import joinedload
    control = db.query(ControlCalidad).options(
        joinedload(ControlCalidad.lote),
        joinedload(ControlCalidad.remision).joinedload(Remision.taller),
        joinedload(ControlCalidad.imperfectos)
    ).filter(ControlCalidad.id == control_id).first()
    if not control:
        raise HTTPException(status_code=404, detail="Control de calidad no encontrado")
    return control

@router.put("/calidad/{control_id}", response_model=ControlCalidadResponse)
def actualizar_control_calidad(control_id: int, control: ControlCalidadUpdate, db: Session = Depends(get_db)):
    db_control = db.query(ControlCalidad).filter(ControlCalidad.id == control_id).first()
    if not db_control:
        raise HTTPException(status_code=404, detail="Control de calidad no encontrado")
    
    update_data = control.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_control, field, value)
    
    # RN-7: Si el estado cambia a "APROBADO", actualizar inventario de PT
    if db_control.estado == EstadoControlCalidad.APROBADO and db_control.cantidad_aprobada > 0:
        try:
            actualizar_inventario_pt_por_calidad(db, db_control.lote_id, db_control.cantidad_aprobada)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error actualizando inventario PT para lote {db_control.lote_id}: {e}")
    
    db.commit()
    db.refresh(db_control)
    
    # Cargar las relaciones para la respuesta
    from sqlalchemy.orm import joinedload
    control_completo = db.query(ControlCalidad).options(
        joinedload(ControlCalidad.lote),
        joinedload(ControlCalidad.remision).joinedload(Remision.taller),
        joinedload(ControlCalidad.imperfectos)
    ).filter(ControlCalidad.id == db_control.id).first()
    
    return control_completo

@router.patch("/calidad/{control_id}/estado", response_model=ControlCalidadResponse)
def actualizar_estado_control_calidad(control_id: int, estado_data: dict, db: Session = Depends(get_db)):
    estado = estado_data.get("estado")
    if isinstance(estado, str):
        estado = EstadoControlCalidad(estado)
    
    db_control = db.query(ControlCalidad).filter(ControlCalidad.id == control_id).first()
    if not db_control:
        raise HTTPException(status_code=404, detail="Control de calidad no encontrado")
    
    db_control.estado = estado
    
    # Actualizar fechas según el estado
    from datetime import datetime
    if estado == EstadoControlCalidad.DEVUELTO_TALLER and not db_control.fecha_devolucion:
        db_control.fecha_devolucion = datetime.now()
    elif estado == EstadoControlCalidad.REPARADO and not db_control.fecha_recepcion_reparado:
        db_control.fecha_recepcion_reparado = datetime.now()
    
    db.commit()
    db.refresh(db_control)
    
    # Cargar las relaciones para la respuesta
    from sqlalchemy.orm import joinedload
    control_completo = db.query(ControlCalidad).options(
        joinedload(ControlCalidad.lote),
        joinedload(ControlCalidad.remision).joinedload(Remision.taller),
        joinedload(ControlCalidad.imperfectos)
    ).filter(ControlCalidad.id == db_control.id).first()
    
    return control_completo

# ========== IMPERFECTOS DE CALIDAD ==========
@router.get("/calidad/{control_id}/imperfectos", response_model=List[ImperfectoCalidadResponse])
def listar_imperfectos_calidad(control_id: int, db: Session = Depends(get_db)):
    return db.query(ImperfectoCalidad).filter(ImperfectoCalidad.control_calidad_id == control_id).all()

@router.post("/calidad/{control_id}/imperfectos", response_model=ImperfectoCalidadResponse, status_code=status.HTTP_201_CREATED)
def crear_imperfecto_calidad(control_id: int, imperfecto: ImperfectoCalidadCreate, db: Session = Depends(get_db)):
    # Verificar que el control de calidad existe
    control = db.query(ControlCalidad).filter(ControlCalidad.id == control_id).first()
    if not control:
        raise HTTPException(status_code=404, detail="Control de calidad no encontrado")
    
    db_imperfecto = ImperfectoCalidad(control_calidad_id=control_id, **imperfecto.model_dump())
    db.add(db_imperfecto)
    db.commit()
    db.refresh(db_imperfecto)
    return db_imperfecto

@router.put("/calidad/imperfectos/{imperfecto_id}", response_model=ImperfectoCalidadResponse)
def actualizar_imperfecto_calidad(imperfecto_id: int, imperfecto: ImperfectoCalidadUpdate, db: Session = Depends(get_db)):
    db_imperfecto = db.query(ImperfectoCalidad).filter(ImperfectoCalidad.id == imperfecto_id).first()
    if not db_imperfecto:
        raise HTTPException(status_code=404, detail="Imperfecto no encontrado")
    
    update_data = imperfecto.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_imperfecto, field, value)
    
    # Actualizar fecha de arreglo si se marca como reparado
    if update_data.get("estado_arreglo") == EstadoControlCalidad.REPARADO:
        from datetime import datetime
        db_imperfecto.fecha_arreglo = datetime.now()
    
    db.commit()
    db.refresh(db_imperfecto)
    return db_imperfecto

@router.delete("/calidad/imperfectos/{imperfecto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_imperfecto_calidad(imperfecto_id: int, db: Session = Depends(get_db)):
    imperfecto = db.query(ImperfectoCalidad).filter(ImperfectoCalidad.id == imperfecto_id).first()
    if not imperfecto:
        raise HTTPException(status_code=404, detail="Imperfecto no encontrado")
    
    db.delete(imperfecto)
    db.commit()
    return None