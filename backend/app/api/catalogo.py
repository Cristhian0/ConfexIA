from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models import Talla, Color, Material, Referencia
from app.schemas.catalogo import (
    TallaCreate, TallaUpdate, TallaResponse,
    ColorCreate, ColorUpdate, ColorResponse,
    MaterialCreate, MaterialUpdate, MaterialResponse,
    ReferenciaCreate, ReferenciaUpdate, ReferenciaResponse
)

router = APIRouter()

# ========== TALLAS ==========
@router.get("/tallas", response_model=List[TallaResponse])
def listar_tallas(skip: int = 0, limit: int = 100, activo: bool = None, db: Session = Depends(get_db)):
    query = db.query(Talla)
    if activo is not None:
        query = query.filter(Talla.activo == activo)
    return query.offset(skip).limit(limit).all()

@router.post("/tallas", response_model=TallaResponse, status_code=status.HTTP_201_CREATED)
def crear_talla(talla: TallaCreate, db: Session = Depends(get_db)):
    db_talla = Talla(**talla.model_dump())
    db.add(db_talla)
    db.commit()
    db.refresh(db_talla)
    return db_talla

@router.get("/tallas/{talla_id}", response_model=TallaResponse)
def obtener_talla(talla_id: int, db: Session = Depends(get_db)):
    talla = db.query(Talla).filter(Talla.id == talla_id).first()
    if not talla:
        raise HTTPException(status_code=404, detail="Talla no encontrada")
    return talla

@router.put("/tallas/{talla_id}", response_model=TallaResponse)
def actualizar_talla(talla_id: int, talla: TallaUpdate, db: Session = Depends(get_db)):
    db_talla = db.query(Talla).filter(Talla.id == talla_id).first()
    if not db_talla:
        raise HTTPException(status_code=404, detail="Talla no encontrada")
    update_data = talla.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_talla, field, value)
    db.commit()
    db.refresh(db_talla)
    return db_talla

@router.delete("/tallas/{talla_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_talla(talla_id: int, db: Session = Depends(get_db)):
    talla = db.query(Talla).filter(Talla.id == talla_id).first()
    if not talla:
        raise HTTPException(status_code=404, detail="Talla no encontrada")
    db.delete(talla)
    db.commit()
    return None

# ========== COLORES ==========
@router.get("/colores", response_model=List[ColorResponse])
def listar_colores(skip: int = 0, limit: int = 100, activo: bool = None, db: Session = Depends(get_db)):
    query = db.query(Color)
    if activo is not None:
        query = query.filter(Color.activo == activo)
    return query.offset(skip).limit(limit).all()

@router.post("/colores", response_model=ColorResponse, status_code=status.HTTP_201_CREATED)
def crear_color(color: ColorCreate, db: Session = Depends(get_db)):
    db_color = Color(**color.model_dump())
    db.add(db_color)
    db.commit()
    db.refresh(db_color)
    return db_color

@router.get("/colores/{color_id}", response_model=ColorResponse)
def obtener_color(color_id: int, db: Session = Depends(get_db)):
    color = db.query(Color).filter(Color.id == color_id).first()
    if not color:
        raise HTTPException(status_code=404, detail="Color no encontrado")
    return color

@router.put("/colores/{color_id}", response_model=ColorResponse)
def actualizar_color(color_id: int, color: ColorUpdate, db: Session = Depends(get_db)):
    db_color = db.query(Color).filter(Color.id == color_id).first()
    if not db_color:
        raise HTTPException(status_code=404, detail="Color no encontrado")
    update_data = color.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_color, field, value)
    db.commit()
    db.refresh(db_color)
    return db_color

@router.delete("/colores/{color_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_color(color_id: int, db: Session = Depends(get_db)):
    color = db.query(Color).filter(Color.id == color_id).first()
    if not color:
        raise HTTPException(status_code=404, detail="Color no encontrado")
    db.delete(color)
    db.commit()
    return None

# ========== MATERIALES ==========
@router.get("/materiales", response_model=List[MaterialResponse])
def listar_materiales(skip: int = 0, limit: int = 100, activo: bool = None, db: Session = Depends(get_db)):
    query = db.query(Material)
    if activo is not None:
        query = query.filter(Material.activo == activo)
    return query.offset(skip).limit(limit).all()

@router.post("/materiales", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
def crear_material(material: MaterialCreate, db: Session = Depends(get_db)):
    db_material = Material(**material.model_dump())
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material

@router.get("/materiales/{material_id}", response_model=MaterialResponse)
def obtener_material(material_id: int, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material no encontrado")
    return material

@router.put("/materiales/{material_id}", response_model=MaterialResponse)
def actualizar_material(material_id: int, material: MaterialUpdate, db: Session = Depends(get_db)):
    db_material = db.query(Material).filter(Material.id == material_id).first()
    if not db_material:
        raise HTTPException(status_code=404, detail="Material no encontrado")
    update_data = material.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_material, field, value)
    db.commit()
    db.refresh(db_material)
    return db_material

@router.delete("/materiales/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_material(material_id: int, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material no encontrado")
    db.delete(material)
    db.commit()
    return None

# ========== REFERENCIAS ==========
@router.get("/referencias", response_model=List[ReferenciaResponse])
def listar_referencias(skip: int = 0, limit: int = 100, activo: bool = None, db: Session = Depends(get_db)):
    query = db.query(Referencia)
    if activo is not None:
        query = query.filter(Referencia.activo == activo)
    return query.offset(skip).limit(limit).all()

@router.post("/referencias", response_model=ReferenciaResponse, status_code=status.HTTP_201_CREATED)
def crear_referencia(referencia: ReferenciaCreate, db: Session = Depends(get_db)):
    db_referencia = Referencia(**referencia.model_dump())
    db.add(db_referencia)
    db.commit()
    db.refresh(db_referencia)
    return db_referencia

@router.get("/referencias/{referencia_id}", response_model=ReferenciaResponse)
def obtener_referencia(referencia_id: int, db: Session = Depends(get_db)):
    referencia = db.query(Referencia).filter(Referencia.id == referencia_id).first()
    if not referencia:
        raise HTTPException(status_code=404, detail="Referencia no encontrada")
    return referencia

@router.put("/referencias/{referencia_id}", response_model=ReferenciaResponse)
def actualizar_referencia(referencia_id: int, referencia: ReferenciaUpdate, db: Session = Depends(get_db)):
    db_referencia = db.query(Referencia).filter(Referencia.id == referencia_id).first()
    if not db_referencia:
        raise HTTPException(status_code=404, detail="Referencia no encontrada")
    update_data = referencia.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_referencia, field, value)
    db.commit()
    db.refresh(db_referencia)
    return db_referencia

@router.delete("/referencias/{referencia_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_referencia(referencia_id: int, db: Session = Depends(get_db)):
    referencia = db.query(Referencia).filter(Referencia.id == referencia_id).first()
    if not referencia:
        raise HTTPException(status_code=404, detail="Referencia no encontrada")
    db.delete(referencia)
    db.commit()
    return None

