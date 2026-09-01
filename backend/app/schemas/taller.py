from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.taller import EstadoRemision
from app.schemas.lote import LoteResponse
from app.schemas.catalogo import TallaResponse

# Taller Schemas
class TallerBase(BaseModel):
    codigo: str = Field(..., max_length=20)
    nombre: str = Field(..., max_length=200)
    direccion: Optional[str] = Field(None, max_length=500)
    telefono: Optional[str] = Field(None, max_length=20)
    contacto: Optional[str] = Field(None, max_length=200)
    activo: bool = True
    capacidad_diaria: int = Field(0, ge=0)

class TallerCreate(TallerBase):
    pass

class TallerUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=20)
    nombre: Optional[str] = Field(None, max_length=200)
    direccion: Optional[str] = Field(None, max_length=500)
    telefono: Optional[str] = Field(None, max_length=20)
    contacto: Optional[str] = Field(None, max_length=200)
    activo: Optional[bool] = None
    capacidad_diaria: Optional[int] = Field(None, ge=0)

class TallerResponse(TallerBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# RemisionDetalle Schemas
class RemisionDetalleBase(BaseModel):
    talla_id: int
    cantidad: int = Field(..., ge=0)
    confeccionista_nombre: Optional[str] = None
    tipo_prenda: Optional[str] = None
    fecha_entrega_estimada: Optional[datetime] = None

class RemisionDetalleCreate(RemisionDetalleBase):
    
    pass

class RemisionDetalleUpdate(BaseModel):
    talla_id: Optional[int] = None
    cantidad: Optional[int] = Field(None, ge=0)
    cantidad_recibida: Optional[int] = Field(None, ge=0)
    cantidad_entregada: Optional[int] = Field(None, ge=0)
    confeccionista_nombre: Optional[str] = None
    tipo_prenda: Optional[str] = None
    fecha_entrega_estimada: Optional[datetime] = None

class RemisionDetalleResponse(RemisionDetalleBase):
    id: int
    remision_id: int
    cantidad_recibida: int
    cantidad_entregada: int
    confeccionista_nombre: Optional[str] = None
    tipo_prenda: Optional[str] = None
    fecha_entrega_estimada: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    # Relaciones opcionales
    talla: Optional[TallaResponse] = None  
    
    class Config:
        from_attributes = True

# Remision Schemas
class RemisionBase(BaseModel):
    numero_remision: str = Field(..., max_length=50)
    lote_id: int
    taller_id: int
    fecha_remision: datetime
    fecha_entrega_estimada: Optional[datetime] = None
    observaciones: Optional[str] = Field(None, max_length=500)

class RemisionCreate(RemisionBase):
    estado: Optional[EstadoRemision] = EstadoRemision.PENDIENTE
    detalles: List[RemisionDetalleCreate]

class RemisionUpdate(BaseModel):
    numero_remision: Optional[str] = Field(None, max_length=50)
    lote_id: Optional[int] = None
    taller_id: Optional[int] = None
    fecha_remision: Optional[datetime] = None
    fecha_entrega_estimada: Optional[datetime] = None
    fecha_recepcion: Optional[datetime] = None
    revisado_por: Optional[str] = Field(None, max_length=200)
    estado: Optional[EstadoRemision] = None
    observaciones: Optional[str] = Field(None, max_length=500)

class RemisionResponse(RemisionBase):
    id: int
    estado: EstadoRemision
    fecha_recepcion: Optional[datetime] = None
    revisado_por: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    detalles: List[RemisionDetalleResponse] = []
    # Relaciones opcionales (solo si están cargadas con joinedload)
    taller: Optional[TallerResponse] = None
    lote: Optional[LoteResponse] = None  # Para incluir información básica del lote si está cargada
    
    class Config:
        from_attributes = True

