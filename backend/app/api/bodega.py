from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.producto_terminado import (
    ProductoTerminadoStock,
    ProductoTerminadoMovimiento,
    TipoMovimientoProductoTerminado,
)
from app.schemas.producto_terminado import (
    ProductoTerminadoStockResponse,
    ProductoTerminadoSalidaCreate,
)

router = APIRouter()


@router.get("/stock", response_model=List[ProductoTerminadoStockResponse])
def listar_stock(
    sku: Optional[str] = None,
    tipo: Optional[str] = None,
    talla_id: Optional[int] = None,
    color_id: Optional[int] = None,
    zona: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(ProductoTerminadoStock)

    if sku:
        query = query.filter(ProductoTerminadoStock.sku.ilike(f"%{sku}%"))
    if tipo:
        query = query.filter(ProductoTerminadoStock.tipo.ilike(f"%{tipo}%"))
    if talla_id is not None:
        query = query.filter(ProductoTerminadoStock.talla_id == talla_id)
    if color_id is not None:
        query = query.filter(ProductoTerminadoStock.color_id == color_id)
    if zona is not None:
        query = query.filter(ProductoTerminadoStock.zona == zona)

    return query.order_by(ProductoTerminadoStock.id.desc()).all()


@router.get("/stock/{stock_id}", response_model=ProductoTerminadoStockResponse)
def obtener_stock(stock_id: int, db: Session = Depends(get_db)):
    stock = db.query(ProductoTerminadoStock).filter(ProductoTerminadoStock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock de producto terminado no encontrado")
    return stock


@router.post("/stock/{stock_id}/salida", response_model=ProductoTerminadoStockResponse, status_code=status.HTTP_200_OK)
def registrar_salida(stock_id: int, data: ProductoTerminadoSalidaCreate, db: Session = Depends(get_db)):
    stock = db.query(ProductoTerminadoStock).filter(ProductoTerminadoStock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock de producto terminado no encontrado")

    if data.cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad de salida debe ser mayor que cero")

    if data.cantidad > stock.cantidad_actual:
        raise HTTPException(
            status_code=400,
            detail=f"Stock insuficiente: disponible {stock.cantidad_actual}, solicitado {data.cantidad}."
        )

    stock.cantidad_actual -= data.cantidad

    movimiento = ProductoTerminadoMovimiento(
        producto_stock_id=stock.id,
        tipo=TipoMovimientoProductoTerminado.SALIDA,
        cantidad=data.cantidad,
        descripcion=data.descripcion,
    )

    db.add(movimiento)
    db.commit()
    db.refresh(stock)
    return stock
