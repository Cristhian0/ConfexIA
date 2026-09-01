from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, date
from app.models.colilla import EstadoColilla, TipoTrabajo


# ========== COLILLA Schemas ==========
class ColillaBase(BaseModel):
    """Base schema para Colilla"""
    lote_id: int
    taller_id: int
    confeccionista_nombre: str = Field(..., max_length=200)
    confeccionista_cedula: Optional[str] = Field(None, max_length=20)
    tipo_trabajo: TipoTrabajo
    cantidad_prendas: int = Field(..., ge=0)
    descripcion_trabajo: Optional[str] = None
    referencia: Optional[str] = Field(None, max_length=100)
    talla_id: Optional[int] = None
    color: Optional[str] = Field(None, max_length=100)
    fecha_limite_entrega: Optional[date] = None
    observaciones: Optional[str] = None
    remision_detalle_id: Optional[int] = None
    firma_base64: Optional[str] = None

    @field_validator('talla_id', mode='before')
    def validate_talla_id(cls, v):
        if v == '' or v == 'null':
            return None
        return v

    @field_validator('fecha_limite_entrega', mode='before')
    def validate_fecha_limite(cls, v):
        if v == '' or v == 'null':
            return None
        return v


class ColillaCreate(ColillaBase):
    """Schema para crear una Colilla"""
    pass


class ColillaUpdate(BaseModel):
    """Schema para actualizar una Colilla"""
    confeccionista_nombre: Optional[str] = Field(None, max_length=200)
    confeccionista_cedula: Optional[str] = Field(None, max_length=20)
    cantidad_completada: Optional[int] = Field(None, ge=0)
    cantidad_rechazada: Optional[int] = Field(None, ge=0)
    estado: Optional[EstadoColilla] = None
    fecha_completacion: Optional[datetime] = None
    observaciones: Optional[str] = None


class ColillaStatusUpdate(BaseModel):
    """Schema para actualizar estado de Colilla"""
    estado: EstadoColilla
    cantidad_completada: Optional[int] = Field(None, ge=0)
    cantidad_rechazada: Optional[int] = Field(None, ge=0)
    observaciones: Optional[str] = None


class ColillaResponse(ColillaBase):
    """Schema de respuesta para Colilla"""
    id: int
    numero_colilla: str
    cantidad_completada: int
    cantidad_rechazada: int
    estado: EstadoColilla
    fecha_creacion: datetime
    fecha_asignacion: Optional[datetime] = None
    fecha_completacion: Optional[datetime] = None
    activa: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    firma_base64: Optional[str] = None
    
    class Config:
        from_attributes = True


class ColillaListResponse(BaseModel):
    """Schema para listar colillas (versión reducida)"""
    id: int
    numero_colilla: str
    confeccionista_nombre: str
    tipo_trabajo: TipoTrabajo
    cantidad_prendas: int
    cantidad_completada: int
    estado: EstadoColilla
    fecha_creacion: datetime
    fecha_limite_entrega: Optional[date] = None
    firma_base64: Optional[str] = None
    
    class Config:
        from_attributes = True


class ColillaExportRequest(BaseModel):
    """Schema para exportar colillas a PDF"""
    colilla_ids: List[int] = Field(..., min_items=1)
    include_completed: bool = False


class ColillaFirmaPDFRequest(BaseModel):
    """Schema para generar PDF de una colilla con firma"""
    firma_base64: str


class ColillaImportar(BaseModel):
    """Schema para importar colillas desde PDF"""
    archivo: str  # Base64 encoded PDF
    taller_id: int
