from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Talla Schemas
class TallaBase(BaseModel):
    codigo: str = Field(..., max_length=10)
    nombre: str = Field(..., max_length=50)
    activo: bool = True

class TallaCreate(TallaBase):
    pass

class TallaUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=10)
    nombre: Optional[str] = Field(None, max_length=50)
    activo: Optional[bool] = None

class TallaResponse(TallaBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Color Schemas
class ColorBase(BaseModel):
    codigo: str = Field(..., max_length=20)
    nombre: str = Field(..., max_length=100)
    color_hex: Optional[str] = Field(None, max_length=7)
    activo: bool = True

class ColorCreate(ColorBase):
    pass

class ColorUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=20)
    nombre: Optional[str] = Field(None, max_length=100)
    color_hex: Optional[str] = Field(None, max_length=7)
    activo: Optional[bool] = None

class ColorResponse(ColorBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Material Schemas
class MaterialBase(BaseModel):
    codigo: str = Field(..., max_length=20)
    nombre: str = Field(..., max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    activo: bool = True

class MaterialCreate(MaterialBase):
    pass

class MaterialUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=20)
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    activo: Optional[bool] = None

class MaterialResponse(MaterialBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Referencia Schemas
class ReferenciaBase(BaseModel):
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=200)
    descripcion: Optional[str] = Field(None, max_length=500)
    es_pedido_especial: bool = False
    activo: bool = True

class ReferenciaCreate(ReferenciaBase):
    pass

class ReferenciaUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=50)
    nombre: Optional[str] = Field(None, max_length=200)
    descripcion: Optional[str] = Field(None, max_length=500)
    es_pedido_especial: Optional[bool] = None
    activo: Optional[bool] = None

class ReferenciaResponse(ReferenciaBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

