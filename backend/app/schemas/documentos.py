from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from app.models.documentos import ZonaAlmacen, TipoMovimientoFinanciero


class NOCBase(BaseModel):
    numero_noc: str = Field(..., max_length=50)
    lote_id: int
    remision_id: int
    observaciones: Optional[str] = Field(None, max_length=500)


class NOCCreate(NOCBase):
    fecha_generacion: Optional[datetime] = None


class NOCResponse(NOCBase):
    id: int
    fecha_generacion: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlmacenamientoZonaBase(BaseModel):
    zona: ZonaAlmacen
    almacenado_por: Optional[str] = Field(None, max_length=200)
    fecha_asignacion: Optional[datetime] = None


class AlmacenamientoZonaCreate(AlmacenamientoZonaBase):
    noc_id: int


class AlmacenamientoZonaResponse(AlmacenamientoZonaBase):
    id: int
    noc_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FinancieroRegistroBase(BaseModel):
    tipo: TipoMovimientoFinanciero
    monto: Decimal = Field(..., ge=0)
    descripcion: Optional[str] = Field(None, max_length=1000)
    fecha_registro: Optional[datetime] = None


class FinancieroRegistroCreate(FinancieroRegistroBase):
    noc_id: int


class FinancieroRegistroResponse(FinancieroRegistroBase):
    id: int
    noc_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

