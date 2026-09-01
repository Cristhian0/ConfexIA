from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

from app.models.bodega import TipoMovimientoRollo


class RolloStockBase(BaseModel):
    material_id: int
    color_id: int
    lote_proveedor: Optional[str] = Field(None, max_length=50)
    cantidad_actual: Decimal = Field(..., ge=0)
    cantidad_reservada: Decimal = Field(0, ge=0)


class RolloStockResponse(RolloStockBase):
    id: int
    material_nombre: Optional[str] = None
    color_nombre: Optional[str] = None
    lote_proveedor: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RolloMovimientoCreate(BaseModel):
    material_id: int
    color_id: int
    cantidad: Decimal = Field(..., ge=0)
    orden_corte_id: Optional[int] = None
    descripcion: Optional[str] = Field(None, max_length=1000)


class IngresoRolloCreate(RolloMovimientoCreate):
    lote_proveedor: str = Field(..., max_length=50)


class SalidaRolloCreate(RolloMovimientoCreate):
    pass


class RolloMovimientoResponse(BaseModel):
    id: int
    rollo_stock_id: int
    tipo: TipoMovimientoRollo
    cantidad: Decimal
    orden_corte_id: Optional[int] = None
    descripcion: Optional[str] = None
    fecha_movimiento: datetime

    class Config:
        from_attributes = True


class ListaStockResponse(BaseModel):
    items: List[RolloStockResponse] = []

