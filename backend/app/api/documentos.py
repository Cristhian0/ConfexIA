from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.models import Lote, Remision
from app.models.documentos import (
    NOC,
    AlmacenamientoZona,
    FinancieroRegistro,
    ZonaAlmacen,
    TipoMovimientoFinanciero,
)
from app.schemas.documentos import (
    NOCCreate,
    NOCResponse,
    AlmacenamientoZonaCreate,
    AlmacenamientoZonaResponse,
    FinancieroRegistroCreate,
    FinancieroRegistroResponse,
)
from app.core.business_rules import recalcular_costo_unitario_lote


router = APIRouter()


@router.post("/noc", response_model=NOCResponse, status_code=status.HTTP_201_CREATED)
def crear_noc(noc: NOCCreate, db: Session = Depends(get_db)):
    # Evitar duplicados del número de NOC
    existente = db.query(NOC).filter(NOC.numero_noc == noc.numero_noc).first()
    if existente:
        raise HTTPException(status_code=400, detail="El número de NOC ya existe")

    lote = db.query(Lote).filter(Lote.id == noc.lote_id).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")

    remision = db.query(Remision).filter(Remision.id == noc.remision_id).first()
    if not remision:
        raise HTTPException(status_code=404, detail="Remisión no encontrada")

    # Si el remision pertenece a otro lote, lo rechazamos para consistencia
    if hasattr(remision, "lote_id") and remision.lote_id != noc.lote_id:
        raise HTTPException(status_code=400, detail="La remisión no corresponde al lote indicado")

    noc_data = noc.model_dump()
    if noc_data.get("fecha_generacion") is None:
        noc_data["fecha_generacion"] = datetime.now()

    db_noc = NOC(**noc_data)
    db.add(db_noc)
    db.commit()
    db.refresh(db_noc)
    return db_noc


@router.get("/noc", response_model=List[NOCResponse])
def listar_noc(
    remision_id: Optional[int] = None,
    lote_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(NOC)
    if remision_id is not None:
        query = query.filter(NOC.remision_id == remision_id)
    if lote_id is not None:
        query = query.filter(NOC.lote_id == lote_id)
    return query.order_by(NOC.fecha_generacion.desc()).all()


@router.get("/noc/{noc_id}/almacenamiento", response_model=List[AlmacenamientoZonaResponse])
def listar_almacenamiento(noc_id: int, db: Session = Depends(get_db)):
    return (
        db.query(AlmacenamientoZona)
        .filter(AlmacenamientoZona.noc_id == noc_id)
        .order_by(AlmacenamientoZona.fecha_asignacion.desc())
        .all()
    )


@router.post("/noc/{noc_id}/almacenamiento", response_model=AlmacenamientoZonaResponse, status_code=status.HTTP_201_CREATED)
def crear_almacenamiento(
    noc_id: int,
    data: AlmacenamientoZonaCreate,
    db: Session = Depends(get_db),
):
    if data.noc_id != noc_id:
        raise HTTPException(status_code=400, detail="noc_id no coincide en la ruta y el body")

    noc = db.query(NOC).filter(NOC.id == noc_id).first()
    if not noc:
        raise HTTPException(status_code=404, detail="NOC no encontrada")

    # Permitir solo un registro por NOC (por diseño; columna unique en DB)
    existente = db.query(AlmacenamientoZona).filter(AlmacenamientoZona.noc_id == noc_id).first()
    if existente:
        raise HTTPException(status_code=400, detail="Este NOC ya tiene almacenamiento asignado")

    almacen_data = data.model_dump()
    if almacen_data.get("fecha_asignacion") is None:
        almacen_data["fecha_asignacion"] = datetime.now()

    db_alm = AlmacenamientoZona(**almacen_data)
    db.add(db_alm)
    db.commit()
    db.refresh(db_alm)
    return db_alm


@router.get("/noc/{noc_id}/financiero", response_model=List[FinancieroRegistroResponse])
def listar_financiero(noc_id: int, db: Session = Depends(get_db)):
    return (
        db.query(FinancieroRegistro)
        .filter(FinancieroRegistro.noc_id == noc_id)
        .order_by(FinancieroRegistro.fecha_registro.desc())
        .all()
    )


@router.post("/noc/{noc_id}/financiero", response_model=FinancieroRegistroResponse, status_code=status.HTTP_201_CREATED)
def crear_financiero(
    noc_id: int,
    data: FinancieroRegistroCreate,
    db: Session = Depends(get_db),
):
    if data.noc_id != noc_id:
        raise HTTPException(status_code=400, detail="noc_id no coincide en la ruta y el body")

    noc = db.query(NOC).filter(NOC.id == noc_id).first()
    if not noc:
        raise HTTPException(status_code=404, detail="NOC no encontrada")

    fin_data = data.model_dump()
    if fin_data.get("fecha_registro") is None:
        fin_data["fecha_registro"] = datetime.now()

    db_fin = FinancieroRegistro(**fin_data)
    db.add(db_fin)
    db.flush()
    
    # RN-4: Recalcular costo unitario del lote si cambian costos de tela, insumos o mano de obra
    try:
        if noc.lote_id:
            recalcular_costo_unitario_lote(db, noc.lote_id)
    except Exception as e:
        # Log del error pero no bloquear la creación
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Error recalculando costo unitario para lote {noc.lote_id}: {e}")
    
    db.commit()
    db.refresh(db_fin)
    return db_fin

