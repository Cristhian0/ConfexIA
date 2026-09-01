from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.models import Color, Talla
from app.models.producto_terminado import (
    ProductoTerminadoStock,
    ProductoTerminadoMovimiento,
    TipoMovimientoProductoTerminado,
)
from app.schemas.producto_terminado import (
    ProductoTerminadoStockResponse,
    ProductoTerminadoStockCreate,
    ProductoTerminadoStockUpdate,
    ProductoTerminadoMovimientoResponse,
)
from app.models.documentos import ZonaAlmacen

router = APIRouter()


@router.get("/stock", response_model=List[ProductoTerminadoStockResponse])
def listar_stock(
    sku: Optional[str] = None,
    tipo: Optional[str] = None,
    talla_id: Optional[int] = None,
    color_id: Optional[int] = None,
    zona: Optional[ZonaAlmacen] = None,
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


@router.post("/stock/ingreso", response_model=ProductoTerminadoStockResponse, status_code=status.HTTP_201_CREATED)
def ingresar_stock(data: ProductoTerminadoStockCreate, db: Session = Depends(get_db)):
    talla = db.query(Talla).filter(Talla.id == data.talla_id).first()
    if not talla:
        raise HTTPException(status_code=404, detail="Talla no encontrada")

    color = db.query(Color).filter(Color.id == data.color_id).first()
    if not color:
        raise HTTPException(status_code=404, detail="Color no encontrado")

    stock = db.query(ProductoTerminadoStock).filter(ProductoTerminadoStock.sku == data.sku).first()
    if stock:
        if stock.tipo != data.tipo or stock.talla_id != data.talla_id or stock.color_id != data.color_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El SKU existe con tipo, talla o color diferente. Usa un SKU único o actualiza el stock existente."
            )
        stock.cantidad_actual += data.cantidad_actual
        stock.zona = data.zona
    else:
        stock = ProductoTerminadoStock(
            sku=data.sku,
            tipo=data.tipo,
            talla_id=data.talla_id,
            color_id=data.color_id,
            zona=data.zona,
            cantidad_actual=data.cantidad_actual,
        )
        db.add(stock)
        db.flush()

    movimiento = ProductoTerminadoMovimiento(
        producto_stock_id=stock.id,
        tipo=TipoMovimientoProductoTerminado.INGRESO,
        cantidad=data.cantidad_actual,
        descripcion=data.descripcion,
    )
    db.add(movimiento)
    db.commit()
    db.refresh(stock)
    return stock


@router.patch("/stock/{stock_id}", response_model=ProductoTerminadoStockResponse)
def actualizar_stock(stock_id: int, data: ProductoTerminadoStockUpdate, db: Session = Depends(get_db)):
    stock = db.query(ProductoTerminadoStock).filter(ProductoTerminadoStock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock de producto terminado no encontrado")

    if data.zona is not None:
        stock.zona = data.zona
    if data.cantidad_actual is not None:
        stock.cantidad_actual = data.cantidad_actual

    db.commit()
    db.refresh(stock)
    return stock


@router.get("/stock/{stock_id}/movimientos", response_model=List[ProductoTerminadoMovimientoResponse])
def listar_movimientos(stock_id: int, db: Session = Depends(get_db)):
    stock = db.query(ProductoTerminadoStock).filter(ProductoTerminadoStock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock de producto terminado no encontrado")

    return (
        db.query(ProductoTerminadoMovimiento)
        .filter(ProductoTerminadoMovimiento.producto_stock_id == stock_id)
        .order_by(ProductoTerminadoMovimiento.fecha_movimiento.desc())
        .all()
    )
