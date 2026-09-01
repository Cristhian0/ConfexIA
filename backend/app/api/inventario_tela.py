from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from app.db.database import get_db
from app.models import Material, Color
from app.models.bodega import (
    RolloStock,
    RolloMovimiento,
    TipoMovimientoRollo,
)
from app.schemas.bodega import (
    RolloStockResponse,
    RolloMovimientoResponse,
    IngresoRolloCreate,
    SalidaRolloCreate,
)
from app.core.business_rules import validar_metros_positivos_tela


router = APIRouter()


def _get_or_create_rollo_stock(db: Session, material_id: int, color_id: int, lote_proveedor: str = None) -> RolloStock:
    stock = db.query(RolloStock).filter(
        RolloStock.material_id == material_id,
        RolloStock.color_id == color_id,
        RolloStock.lote_proveedor == lote_proveedor,
    ).first()
    if stock:
        return stock

    stock = RolloStock(material_id=material_id, color_id=color_id, lote_proveedor=lote_proveedor, cantidad_actual=0)
    db.add(stock)
    db.flush()
    return stock


def _get_stock_or_404(db: Session, material_id: int, color_id: int) -> RolloStock:
    stock = db.query(RolloStock).filter(
        RolloStock.material_id == material_id,
        RolloStock.color_id == color_id,
    ).first()
    if not stock:
        raise HTTPException(status_code=404, detail="No existe stock para ese material/color")
    return stock


@router.get("/rollos/stock", response_model=List[RolloStockResponse])
def listar_stock(
    tipo: Optional[str] = None,
    color: Optional[str] = None,
    lote: Optional[str] = None,
    db: Session = Depends(get_db),
):
    # Se unen para devolver nombres, pero el modelo lo soporta aunque no tengas back_populates
    query = (
        db.query(RolloStock, Material.nombre.label("material_nombre"), Color.nombre.label("color_nombre"))
        .join(Material, Material.id == RolloStock.material_id)
        .join(Color, Color.id == RolloStock.color_id)
    )
    if tipo:
        query = query.filter(Material.nombre.ilike(f"%{tipo}%"))
    if color:
        query = query.filter(Color.nombre.ilike(f"%{color}%"))
    if lote:
        query = query.filter(RolloStock.lote_proveedor.ilike(f"%{lote}%"))

    items = query.order_by(RolloStock.id.desc()).all()

    result: List[RolloStockResponse] = []
    for stock, material_nombre, color_nombre in items:
        result.append(
            RolloStockResponse(
                id=stock.id,
                material_id=stock.material_id,
                color_id=stock.color_id,
                cantidad_actual=stock.cantidad_actual,
                cantidad_reservada=stock.cantidad_reservada,
                material_nombre=material_nombre,
                color_nombre=color_nombre,
                lote_proveedor=stock.lote_proveedor,
                created_at=stock.created_at,
                updated_at=stock.updated_at,
            )
        )
    return result


@router.post("/rollos/ingreso", response_model=RolloMovimientoResponse, status_code=status.HTTP_201_CREATED)
def ingresar_rollos(data: IngresoRolloCreate, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == data.material_id, Material.activo == True).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material no encontrado")

    color = db.query(Color).filter(Color.id == data.color_id, Color.activo == True).first()
    if not color:
        raise HTTPException(status_code=404, detail="Color no encontrado")

    stock = _get_or_create_rollo_stock(db, data.material_id, data.color_id, data.lote_proveedor)

    stock.cantidad_actual = stock.cantidad_actual + data.cantidad

    mov = RolloMovimiento(
        rollo_stock_id=stock.id,
        tipo=TipoMovimientoRollo.INGRESO,
        cantidad=data.cantidad,
        orden_corte_id=data.orden_corte_id,
        descripcion=data.descripcion,
    )
    db.add(mov)
    db.commit()
    db.refresh(mov)
    return mov


@router.post("/rollos/salida", response_model=RolloMovimientoResponse, status_code=status.HTTP_201_CREATED)
def sacar_rollos(data: SalidaRolloCreate, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == data.material_id, Material.activo == True).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material no encontrado")

    color = db.query(Color).filter(Color.id == data.color_id, Color.activo == True).first()
    if not color:
        raise HTTPException(status_code=404, detail="Color no encontrado")

    # RN-3: Validar que hay suficiente stock total disponible
    validar_metros_positivos_tela(
        db,
        data.material_id,
        data.color_id,
        data.cantidad,
        None  # No especificamos lote_proveedor para validar el total disponible
    )

    # Obtener todos los stocks disponibles para este material/color, ordenados por fecha de creación (FIFO)
    stocks_disponibles = db.query(RolloStock).filter(
        RolloStock.material_id == data.material_id,
        RolloStock.color_id == data.color_id,
        RolloStock.cantidad_actual > 0
    ).order_by(RolloStock.created_at).all()

    if not stocks_disponibles:
        raise HTTPException(status_code=404, detail=f"No hay stock disponible para material_id={data.material_id}, color_id={data.color_id}")

    # Descontar de los stocks disponibles (FIFO - First In, First Out)
    cantidad_restante = data.cantidad
    movimientos_creados = []

    for stock in stocks_disponibles:
        if cantidad_restante <= 0:
            break

        # Calcular cuánto descontar de este lote
        cantidad_a_descontar = min(cantidad_restante, stock.cantidad_actual)
        
        # Descontar del stock
        stock.cantidad_actual = stock.cantidad_actual - cantidad_a_descontar
        
        # Crear movimiento para este lote
        mov = RolloMovimiento(
            rollo_stock_id=stock.id,
            tipo=TipoMovimientoRollo.SALIDA,
            cantidad=-cantidad_a_descontar,  # Negativo para indicar salida
            orden_corte_id=data.orden_corte_id,
            descripcion=data.descripcion or f"Salida para Orden de Corte #{data.orden_corte_id}"
        )
        db.add(mov)
        movimientos_creados.append(mov)
        
        cantidad_restante -= cantidad_a_descontar

    db.commit()
    
    # Devolver el último movimiento creado (o el principal si solo hay uno)
    for mov in movimientos_creados:
        db.refresh(mov)
    
    return movimientos_creados[-1]  # Devolver el último movimiento creado


@router.get("/rollos/movimientos", response_model=List[RolloMovimientoResponse])
def listar_movimientos(
    material_id: Optional[int] = None,
    color_id: Optional[int] = None,
    orden_corte_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(RolloMovimiento).join(RolloStock, RolloStock.id == RolloMovimiento.rollo_stock_id)
    if material_id is not None:
        query = query.filter(RolloStock.material_id == material_id)
    if color_id is not None:
        query = query.filter(RolloStock.color_id == color_id)
    if orden_corte_id is not None:
        query = query.filter(RolloMovimiento.orden_corte_id == orden_corte_id)

    return query.order_by(RolloMovimiento.fecha_movimiento.desc()).limit(200).all()

