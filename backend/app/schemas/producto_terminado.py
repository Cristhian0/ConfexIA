from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.models.documentos import ZonaAlmacen
from app.models.producto_terminado import TipoMovimientoProductoTerminado


class ProductoTerminadoStockBase(BaseModel):
    sku: str = Field(..., max_length=100)
    tipo: str = Field(..., max_length=100)
    talla_id: int
    color_id: int
    zona: ZonaAlmacen
    cantidad_actual: int = Field(..., ge=0)


class ProductoTerminadoStockCreate(ProductoTerminadoStockBase):
    descripcion: Optional[str] = Field(None, max_length=500)


class ProductoTerminadoStockUpdate(BaseModel):
    zona: Optional[ZonaAlmacen] = None
    cantidad_actual: Optional[int] = Field(None, ge=0)


class ProductoTerminadoSalidaCreate(BaseModel):
    cantidad: int = Field(..., gt=0)
    descripcion: Optional[str] = Field(None, max_length=500)


class ProductoTerminadoStockResponse(ProductoTerminadoStockBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductoTerminadoMovimientoBase(BaseModel):
    tipo: TipoMovimientoProductoTerminado
    cantidad: int = Field(..., ge=1)
    descripcion: Optional[str] = Field(None, max_length=500)


class ProductoTerminadoMovimientoCreate(ProductoTerminadoMovimientoBase):
    sku: str = Field(..., max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)


class ProductoTerminadoMovimientoResponse(ProductoTerminadoMovimientoBase):
    id: int
    producto_stock_id: int
    fecha_movimiento: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
