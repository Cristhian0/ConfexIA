from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.corte import EstadoOrdenCorte, EstadoReservaTela


class OrdenCorteLineaBase(BaseModel):
    talla_codigo: str = Field(..., min_length=1, max_length=20)
    cantidad: int = Field(..., ge=0)


class OrdenCorteLineaResponse(OrdenCorteLineaBase):
    id: int
    orden_corte_id: int

    class Config:
        from_attributes = True


class OrdenCorteCreate(BaseModel):
    tipo_prenda: str = Field(..., min_length=1, max_length=120)
    lineas: List[OrdenCorteLineaBase] = Field(..., min_length=1)
    numero_orden: Optional[str] = Field(None, max_length=50)
    observaciones: Optional[str] = None


class OrdenCorteUpdateTizado(BaseModel):
    metros_tizado: Optional[Decimal] = None
    rendimiento_pct: Optional[Decimal] = None


class OrdenCorteUpdateCorte(BaseModel):
    piezas_cortadas: Optional[int] = Field(None, ge=0)
    capas_utilizadas: Optional[int] = Field(None, ge=0)


class OrdenCorteUpdateSobrantes(BaseModel):
    metros_sobrante: Optional[Decimal] = None
    metros_desperdicio: Optional[Decimal] = None


class OrdenCorteResponse(BaseModel):
    id: int
    numero_orden: str
    tipo_prenda: str
    estado: EstadoOrdenCorte
    metros_tizado: Optional[Decimal] = None
    rendimiento_pct: Optional[Decimal] = None
    piezas_cortadas: Optional[int] = None
    capas_utilizadas: Optional[int] = None
    metros_sobrante: Optional[Decimal] = None
    metros_desperdicio: Optional[Decimal] = None
    observaciones: Optional[str] = None
    lineas: List[OrdenCorteLineaResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReservaTelaCreate(BaseModel):
    material_id: int
    color_id: int
    metros: Decimal = Field(..., gt=0)
    orden_corte_id: Optional[int] = None
    observaciones: Optional[str] = None


class ReservaTelaResponse(BaseModel):
    id: int
    material_id: int
    color_id: int
    metros: Decimal
    orden_corte_id: Optional[int] = None
    estado: EstadoReservaTela
    observaciones: Optional[str] = None
    material_nombre: Optional[str] = None
    color_nombre: Optional[str] = None
    orden_corte_numero: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
