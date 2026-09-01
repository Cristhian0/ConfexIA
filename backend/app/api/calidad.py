from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models.produccion import InspeccionCalidad, DefectoInspeccion, OrdenProduccion
from app.schemas.produccion import (
    InspeccionCalidadCreate, InspeccionCalidadUpdate, InspeccionCalidadResponse,
    DefectoInspeccionCreate, DefectoInspeccionResponse
)

router = APIRouter()

# ========== RF-15: INSPECCIONES DE CALIDAD ==========
@router.get("/inspecciones", response_model=List[InspeccionCalidadResponse])
def listar_inspecciones(
    skip: int = 0,
    limit: int = 100,
    orden_id: Optional[int] = None,
    clasificacion: Optional[str] = None,
    inspector: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Listar inspecciones de calidad con filtros opcionales"""
    query = db.query(InspeccionCalidad).options(
        joinedload(InspeccionCalidad.defectos)
    )
    
    if orden_id:
        query = query.filter(InspeccionCalidad.orden_produccion_id == orden_id)
    if clasificacion:
        query = query.filter(InspeccionCalidad.clasificacion == clasificacion)
    if inspector:
        query = query.filter(InspeccionCalidad.inspector.ilike(f"%{inspector}%"))
    
    return query.order_by(InspeccionCalidad.fecha_inspeccion.desc()).offset(skip).limit(limit).all()

@router.post("/inspecciones", response_model=InspeccionCalidadResponse, status_code=status.HTTP_201_CREATED)
def crear_inspeccion(inspeccion: InspeccionCalidadCreate, db: Session = Depends(get_db)):
    """RF-15: Crear inspección de calidad para una orden de producción"""
    # Verificar que la orden existe
    orden = db.query(OrdenProduccion).filter(OrdenProduccion.id == inspeccion.orden_produccion_id).first()
    if not orden:
        raise HTTPException(status_code=404, detail="Orden de producción no encontrada")
    
    # Generar número de inspección
    ultimo_numero = db.query(InspeccionCalidad).order_by(InspeccionCalidad.id.desc()).first()
    numero_inspeccion = f"IC-{(ultimo_numero.id + 1) if ultimo_numero else 1:06d}"
    
    # Crear la inspección
    db_inspeccion = InspeccionCalidad(
        numero_inspeccion=numero_inspeccion,
        **inspeccion.dict()
    )
    
    db.add(db_inspeccion)
    db.commit()
    db.refresh(db_inspeccion)
    return db_inspeccion

@router.get("/inspecciones/{inspeccion_id}", response_model=InspeccionCalidadResponse)
def obtener_inspeccion(inspeccion_id: int, db: Session = Depends(get_db)):
    """Obtener una inspección específica"""
    inspeccion = db.query(InspeccionCalidad).options(
        joinedload(InspeccionCalidad.defectos)
    ).filter(InspeccionCalidad.id == inspeccion_id).first()
    
    if not inspeccion:
        raise HTTPException(status_code=404, detail="Inspección no encontrada")
    return inspeccion

@router.patch("/inspecciones/{inspeccion_id}", response_model=InspeccionCalidadResponse)
def actualizar_inspeccion(
    inspeccion_id: int, 
    inspeccion_update: InspeccionCalidadUpdate, 
    db: Session = Depends(get_db)
):
    """RF-16: Actualizar clasificación y resultados de inspección"""
    db_inspeccion = db.query(InspeccionCalidad).filter(InspeccionCalidad.id == inspeccion_id).first()
    
    if not db_inspeccion:
        raise HTTPException(status_code=404, detail="Inspección no encontrada")
    
    update_data = inspeccion_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_inspeccion, field, value)
    
    db.add(db_inspeccion)
    db.commit()
    db.refresh(db_inspeccion)
    return db_inspeccion

@router.get("/inspecciones/{inspeccion_id}/resumen")
def obtener_resumen_inspeccion(inspeccion_id: int, db: Session = Depends(get_db)):
    """Obtener resumen de inspección con porcentajes"""
    inspeccion = db.query(InspeccionCalidad).filter(InspeccionCalidad.id == inspeccion_id).first()
    
    if not inspeccion:
        raise HTTPException(status_code=404, detail="Inspección no encontrada")
    
    total = inspeccion.cantidad_inspeccionada
    if total == 0:
        return {
            "numero_inspeccion": inspeccion.numero_inspeccion,
            "total": 0,
            "porcentaje_ok": 0,
            "porcentaje_reproceso": 0,
            "porcentaje_defectuosa": 0
        }
    
    return {
        "numero_inspeccion": inspeccion.numero_inspeccion,
        "total": total,
        "porcentaje_ok": (inspeccion.cantidad_ok / total) * 100,
        "porcentaje_reproceso": (inspeccion.cantidad_reproceso / total) * 100,
        "porcentaje_defectuosa": (inspeccion.cantidad_defectuosa / total) * 100
    }

# ========== RF-17: DEFECTOS DE INSPECCIÓN ==========
@router.post("/inspecciones/{inspeccion_id}/defectos", response_model=DefectoInspeccionResponse, status_code=status.HTTP_201_CREATED)
def agregar_defecto(
    inspeccion_id: int,
    defecto: DefectoInspeccionCreate,
    db: Session = Depends(get_db)
):
    """RF-17: Agregar defecto encontrado a la inspección"""
    # Verificar que la inspección existe
    inspeccion = db.query(InspeccionCalidad).filter(InspeccionCalidad.id == inspeccion_id).first()
    if not inspeccion:
        raise HTTPException(status_code=404, detail="Inspección no encontrada")
    
    db_defecto = DefectoInspeccion(
        inspeccion_id=inspeccion_id,
        **defecto.dict()
    )
    
    db.add(db_defecto)
    db.commit()
    db.refresh(db_defecto)
    return db_defecto

@router.get("/inspecciones/{inspeccion_id}/defectos", response_model=List[DefectoInspeccionResponse])
def listar_defectos(inspeccion_id: int, db: Session = Depends(get_db)):
    """RF-17: Listar defectos de una inspección"""
    defectos = db.query(DefectoInspeccion).filter(
        DefectoInspeccion.inspeccion_id == inspeccion_id
    ).all()
    return defectos

@router.delete("/defectos/{defecto_id}")
def eliminar_defecto(defecto_id: int, db: Session = Depends(get_db)):
    """RF-17: Eliminar un defecto registrado"""
    defecto = db.query(DefectoInspeccion).filter(DefectoInspeccion.id == defecto_id).first()
    
    if not defecto:
        raise HTTPException(status_code=404, detail="Defecto no encontrado")
    
    db.delete(defecto)
    db.commit()
    return {"message": "Defecto eliminado"}

# ========== RF-18: REINGRESAR A PRODUCCIÓN ==========
@router.post("/inspecciones/{inspeccion_id}/reingresar")
def marcar_reingresar_produccion(inspeccion_id: int, db: Session = Depends(get_db)):
    """RF-18: Marcar inspección para reingresar a producción"""
    inspeccion = db.query(InspeccionCalidad).filter(InspeccionCalidad.id == inspeccion_id).first()
    
    if not inspeccion:
        raise HTTPException(status_code=404, detail="Inspección no encontrada")
    
    # Solo se puede reingresar si tiene reproceso o defectuosa
    if inspeccion.cantidad_reproceso > 0 or inspeccion.cantidad_defectuosa > 0:
        inspeccion.reingresar_produccion = True
        db.add(inspeccion)
        db.commit()
        db.refresh(inspeccion)
        return {
            "message": "Orden reingresada a producción",
            "numero_inspeccion": inspeccion.numero_inspeccion,
            "reingresar_produccion": inspeccion.reingresar_produccion
        }
    else:
        raise HTTPException(
            status_code=400, 
            detail="Solo se pueden reingresar órdenes con reproceso o defectos"
        )

@router.get("/inspecciones/{inspeccion_id}/puede-reingresar")
def verificar_puede_reingresar(inspeccion_id: int, db: Session = Depends(get_db)):
    """RF-18: Verificar si la inspección puede reingresarse a producción"""
    inspeccion = db.query(InspeccionCalidad).filter(InspeccionCalidad.id == inspeccion_id).first()
    
    if not inspeccion:
        raise HTTPException(status_code=404, detail="Inspección no encontrada")
    
    puede_reingresar = inspeccion.cantidad_reproceso > 0 or inspeccion.cantidad_defectuosa > 0
    
    return {
        "numero_inspeccion": inspeccion.numero_inspeccion,
        "puede_reingresar": puede_reingresar,
        "cantidad_reproceso": inspeccion.cantidad_reproceso,
        "cantidad_defectuosa": inspeccion.cantidad_defectuosa
    }
