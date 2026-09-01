from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models import Colilla, Lote, Taller, EstadoColilla
from app.schemas import ColillaCreate, ColillaUpdate, ColillaResponse, ColillaListResponse, ColillaStatusUpdate, ColillaExportRequest, ColillaFirmaPDFRequest
from app.utils.pdf_generator import GeneradorPDFColilla
import os
from io import BytesIO

router = APIRouter()


# ========== COLILLAS - LISTADO Y BÚSQUEDA ==========
@router.get("/", response_model=List[ColillaListResponse])
def listar_colillas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    taller_id: Optional[int] = None,
    lote_id: Optional[int] = None,
    confeccionista_nombre: Optional[str] = None,
    estado: Optional[EstadoColilla] = None,
    activas: bool = True,
    db: Session = Depends(get_db)
):
    """
    Listar colillas con filtros opcionales
    """
    query = db.query(Colilla)
    
    if activas:
        query = query.filter(Colilla.activa == True)
    
    if taller_id:
        query = query.filter(Colilla.taller_id == taller_id)
    
    if lote_id:
        query = query.filter(Colilla.lote_id == lote_id)
    
    if confeccionista_nombre:
        query = query.filter(Colilla.confeccionista_nombre.ilike(f"%{confeccionista_nombre}%"))
    
    if estado:
        query = query.filter(Colilla.estado == estado)
    
    return query.order_by(Colilla.fecha_creacion.desc()).offset(skip).limit(limit).all()


@router.get("/por-confeccionista/{taller_id}", response_model=dict)
def colillas_por_confeccionista(
    taller_id: int,
    estado: Optional[EstadoColilla] = None,
    db: Session = Depends(get_db)
):
    """
    Obtener colillas agrupadas por confeccionista
    """
    query = db.query(Colilla).filter(Colilla.taller_id == taller_id, Colilla.activa == True)
    
    if estado:
        query = query.filter(Colilla.estado == estado)
    
    colillas = query.all()
    
    # Agrupar por confeccionista
    resultado = {}
    for colilla in colillas:
        if colilla.confeccionista_nombre not in resultado:
            resultado[colilla.confeccionista_nombre] = {
                "confeccionista": colilla.confeccionista_nombre,
                "cedula": colilla.confeccionista_cedula,
                "colillas": [],
                "total_prendas": 0,
                "total_completadas": 0,
                "total_rechazadas": 0
            }
        
        resultado[colilla.confeccionista_nombre]["colillas"].append({
            "id": colilla.id,
            "numero_colilla": colilla.numero_colilla,
            "tipo_trabajo": colilla.tipo_trabajo.value,
            "cantidad_prendas": colilla.cantidad_prendas,
            "cantidad_completada": colilla.cantidad_completada,
            "cantidad_rechazada": colilla.cantidad_rechazada,
            "estado": colilla.estado.value,
            "fecha_limite": colilla.fecha_limite_entrega,
        })
        
        resultado[colilla.confeccionista_nombre]["total_prendas"] += colilla.cantidad_prendas
        resultado[colilla.confeccionista_nombre]["total_completadas"] += colilla.cantidad_completada
        resultado[colilla.confeccionista_nombre]["total_rechazadas"] += colilla.cantidad_rechazada
    
    return resultado


# ========== COLILLAS - CRUD ==========
@router.post("/", response_model=ColillaResponse, status_code=status.HTTP_201_CREATED)
def crear_colilla(colilla: ColillaCreate, db: Session = Depends(get_db)):
    """
    Crear una nueva colilla de confección
    """
    # Verificar que el lote existe
    lote = db.query(Lote).filter(Lote.id == colilla.lote_id).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    
    # Verificar que el taller existe
    taller = db.query(Taller).filter(Taller.id == colilla.taller_id).first()
    if not taller:
        raise HTTPException(status_code=404, detail="Taller no encontrado")
    
    # Generar número de colilla único
    ultima_colilla = db.query(Colilla).order_by(Colilla.id.desc()).first()
    numero_secuencial = (ultima_colilla.id + 1) if ultima_colilla else 1
    numero_colilla = f"COL-{taller.codigo}-{numero_secuencial:06d}"
    
    # Crear colilla
    db_colilla = Colilla(
        numero_colilla=numero_colilla,
        **colilla.model_dump()
    )
    db.add(db_colilla)
    db.commit()
    db.refresh(db_colilla)
    return db_colilla


@router.post("/lote/{lote_id}", response_model=List[ColillaResponse], status_code=status.HTTP_201_CREATED)
def crear_colillas_lote(
    lote_id: int,
    colillas_data: List[ColillaCreate],
    db: Session = Depends(get_db)
):
    """
    Crear múltiples colillas para un lote
    """
    lote = db.query(Lote).filter(Lote.id == lote_id).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    
    colillas_creadas = []
    for i, colilla_data in enumerate(colillas_data):
        taller = db.query(Taller).filter(Taller.id == colilla_data.taller_id).first()
        if not taller:
            raise HTTPException(status_code=404, detail=f"Taller {colilla_data.taller_id} no encontrado")
        
        numero_secuencial = len(colillas_creadas) + 1
        numero_colilla = f"COL-{taller.codigo}-{numero_secuencial:06d}"
        
        db_colilla = Colilla(
            numero_colilla=numero_colilla,
            **colilla_data.model_dump()
        )
        db.add(db_colilla)
        colillas_creadas.append(db_colilla)
    
    db.commit()
    for colilla in colillas_creadas:
        db.refresh(colilla)
    
    return colillas_creadas


@router.get("/{colilla_id}", response_model=ColillaResponse)
def obtener_colilla(colilla_id: int, db: Session = Depends(get_db)):
    """
    Obtener una colilla por ID
    """
    colilla = db.query(Colilla).filter(Colilla.id == colilla_id).first()
    if not colilla:
        raise HTTPException(status_code=404, detail="Colilla no encontrada")
    return colilla


@router.put("/{colilla_id}", response_model=ColillaResponse)
def actualizar_colilla(
    colilla_id: int,
    colilla_update: ColillaUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar una colilla
    """
    db_colilla = db.query(Colilla).filter(Colilla.id == colilla_id).first()
    if not db_colilla:
        raise HTTPException(status_code=404, detail="Colilla no encontrada")
    
    update_data = colilla_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_colilla, field, value)
    
    db.commit()
    db.refresh(db_colilla)
    return db_colilla


@router.patch("/{colilla_id}/estado", response_model=ColillaResponse)
def actualizar_estado_colilla(
    colilla_id: int,
    estado_update: ColillaStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar el estado de una colilla
    """
    db_colilla = db.query(Colilla).filter(Colilla.id == colilla_id).first()
    if not db_colilla:
        raise HTTPException(status_code=404, detail="Colilla no encontrada")
    
    db_colilla.estado = estado_update.estado
    
    if estado_update.cantidad_completada is not None:
        db_colilla.cantidad_completada = estado_update.cantidad_completada
    
    if estado_update.cantidad_rechazada is not None:
        db_colilla.cantidad_rechazada = estado_update.cantidad_rechazada
    
    if estado_update.observaciones:
        db_colilla.observaciones = estado_update.observaciones
    
    # Si se marca como completada, agregar fecha de completación
    if estado_update.estado == EstadoColilla.COMPLETADA:
        db_colilla.fecha_completacion = datetime.now()
    
    db.commit()
    db.refresh(db_colilla)
    return db_colilla


@router.delete("/{colilla_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_colilla(colilla_id: int, db: Session = Depends(get_db)):
    """
    Eliminar (desactivar) una colilla
    """
    db_colilla = db.query(Colilla).filter(Colilla.id == colilla_id).first()
    if not db_colilla:
        raise HTTPException(status_code=404, detail="Colilla no encontrada")
    
    db_colilla.activa = False
    db.commit()
    return None


# ========== COLILLAS - ESTADÍSTICAS ==========
@router.get("/stats/taller/{taller_id}", response_model=dict)
def estadisticas_colillas_taller(taller_id: int, db: Session = Depends(get_db)):
    """
    Obtener estadísticas de colillas por taller
    """
    colillas = db.query(Colilla).filter(
        Colilla.taller_id == taller_id,
        Colilla.activa == True
    ).all()
    
    total_colillas = len(colillas)
    total_prendas = sum(c.cantidad_prendas for c in colillas)
    total_completadas = sum(c.cantidad_completada for c in colillas)
    total_rechazadas = sum(c.cantidad_rechazada for c in colillas)
    
    pendientes = len([c for c in colillas if c.estado == EstadoColilla.PENDIENTE])
    en_proceso = len([c for c in colillas if c.estado == EstadoColilla.EN_PROCESO])
    completadas = len([c for c in colillas if c.estado == EstadoColilla.COMPLETADA])
    
    return {
        "total_colillas": total_colillas,
        "total_prendas": total_prendas,
        "total_completadas": total_completadas,
        "total_rechazadas": total_rechazadas,
        "porcentaje_completacion": (total_completadas / total_prendas * 100) if total_prendas > 0 else 0,
        "estado_resumen": {
            "pendientes": pendientes,
            "en_proceso": en_proceso,
            "completadas": completadas
        }
    }


# ========== COLILLAS - GENERACIÓN DE PDFS ==========
@router.get("/pdf/{colilla_id}", response_class=FileResponse)
def descargar_colilla_pdf(colilla_id: int, db: Session = Depends(get_db)):
    """
    Descargar colilla individual en PDF para imprimir
    """
    colilla = db.query(Colilla).filter(Colilla.id == colilla_id).first()
    if not colilla:
        raise HTTPException(status_code=404, detail="Colilla no encontrada")
    
    # Generar PDF
    generador = GeneradorPDFColilla()
    pdf_bytes = generador.generar_colilla_individual(colilla)
    
    # Crear archivo temporal
    from tempfile import NamedTemporaryFile
    temp_file = NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_file.write(pdf_bytes)
    temp_file.close()
    
    return FileResponse(
        path=temp_file.name,
        media_type="application/pdf",
        filename=f"Colilla_{colilla.numero_colilla}.pdf"
    )


@router.post("/pdf/{colilla_id}/firmar", response_class=FileResponse)
def descargar_colilla_pdf_firmada(colilla_id: int, firma_request: ColillaFirmaPDFRequest, db: Session = Depends(get_db)):
    """
    Descargar colilla individual en PDF con la firma incluida
    """
    colilla = db.query(Colilla).filter(Colilla.id == colilla_id).first()
    if not colilla:
        raise HTTPException(status_code=404, detail="Colilla no encontrada")

    generador = GeneradorPDFColilla()
    pdf_bytes = generador.generar_colilla_individual(colilla, firma_base64=firma_request.firma_base64)

    from tempfile import NamedTemporaryFile
    temp_file = NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_file.write(pdf_bytes)
    temp_file.close()

    return FileResponse(
        path=temp_file.name,
        media_type="application/pdf",
        filename=f"Colilla_{colilla.numero_colilla}_firmada.pdf"
    )


@router.post("/pdf/taller/{taller_id}", response_class=FileResponse)
def descargar_colillas_taller_pdf(
    taller_id: int,
    estado: Optional[EstadoColilla] = None,
    db: Session = Depends(get_db)
):
    """
    Descargar resumen de colillas por taller en PDF
    """
    query = db.query(Colilla).filter(
        Colilla.taller_id == taller_id,
        Colilla.activa == True
    )
    
    if estado:
        query = query.filter(Colilla.estado == estado)
    
    colillas = query.all()
    
    if not colillas:
        raise HTTPException(status_code=404, detail="No hay colillas para este taller")
    
    # Generar PDF
    generador = GeneradorPDFColilla()
    pdf_bytes = generador.generar_colillas_por_confeccionista(colillas)
    
    # Crear archivo temporal
    from tempfile import NamedTemporaryFile
    temp_file = NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_file.write(pdf_bytes)
    temp_file.close()
    
    taller = db.query(Taller).filter(Taller.id == taller_id).first()
    
    return FileResponse(
        path=temp_file.name,
        media_type="application/pdf",
        filename=f"Colillas_Taller_{taller.codigo if taller else taller_id}.pdf"
    )


@router.post("/pdf/lote/{lote_id}", response_class=FileResponse)
def descargar_colillas_lote_pdf(lote_id: int, db: Session = Depends(get_db)):
    """
    Descargar todas las colillas de un lote en PDF
    """
    colillas = db.query(Colilla).filter(
        Colilla.lote_id == lote_id,
        Colilla.activa == True
    ).all()
    
    if not colillas:
        raise HTTPException(status_code=404, detail="No hay colillas para este lote")
    
    # Generar PDF
    generador = GeneradorPDFColilla()
    pdf_bytes = generador.generar_colillas_por_confeccionista(colillas)
    
    # Crear archivo temporal
    from tempfile import NamedTemporaryFile
    temp_file = NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_file.write(pdf_bytes)
    temp_file.close()
    
    return FileResponse(
        path=temp_file.name,
        media_type="application/pdf",
        filename=f"Colillas_Lote_{lote_id}.pdf"
    )

