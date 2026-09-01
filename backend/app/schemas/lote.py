from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Any
from datetime import datetime
from app.models.lote import EstadoLote

# LoteDetalle Schemas
class LoteDetalleBase(BaseModel):
    color_nombre: str = Field(..., max_length=100)  # Nombre del color
    talla_id: int
    cantidad: int = Field(..., ge=0)

class LoteDetalleCreate(LoteDetalleBase):
    pass

class LoteDetalleUpdate(BaseModel):
    color_nombre: Optional[str] = Field(None, max_length=100)
    talla_id: Optional[int] = None
    cantidad: Optional[int] = Field(None, ge=0)
    cantidad_cortada: Optional[int] = Field(None, ge=0)
    cantidad_en_taller: Optional[int] = Field(None, ge=0)
    cantidad_confeccionada: Optional[int] = Field(None, ge=0)
    cantidad_entregada: Optional[int] = Field(None, ge=0)

class LoteDetalleResponse(BaseModel):
    id: int
    lote_id: int
    color_nombre: Optional[str] = None  # Opcional para compatibilidad con datos antiguos
    talla_id: int
    cantidad: int
    cantidad_cortada: int
    cantidad_en_taller: int
    cantidad_confeccionada: int
    cantidad_entregada: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Lote Schemas
class LoteBase(BaseModel):
    numero_lote: str = Field(..., max_length=50)
    mesa: Optional[str] = Field(None, max_length=50)
    referencia_nombre: str = Field(..., max_length=200)  # Nombre de la referencia
    material_nombre: str = Field(..., max_length=100)  # Nombre del material
    orden_corte_id: Optional[int] = None  # Asociación con orden de corte
    remision_numero: Optional[str] = None
    confeccionista_nombre: Optional[str] = None
    fecha_entrega: Optional[datetime] = None
    fecha_entrega_estimada: Optional[datetime] = None
    despacha: Optional[bool] = None
    fecha_corte: datetime
    observaciones: Optional[str] = Field(None, max_length=500)
    es_pedido_especial: bool = False
    prioridad: int = Field(0, ge=0, le=2)  # 0=normal, 1=alta, 2=urgente
    cantidad_total_programada: Optional[int] = Field(None, ge=0)

class LoteCreate(LoteBase):
    detalles: List[LoteDetalleCreate]
    
    @field_validator('detalles')
    @classmethod
    def validar_detalles(cls, v):
        for detalle in v:
            if not detalle.color_nombre or not detalle.color_nombre.strip():
                raise ValueError("Todos los detalles deben incluir un nombre de color válido")
        return v

class LoteUpdate(BaseModel):
    numero_lote: Optional[str] = Field(None, max_length=50)
    mesa: Optional[str] = Field(None, max_length=50)
    referencia_nombre: Optional[str] = Field(None, max_length=200)
    material_nombre: Optional[str] = Field(None, max_length=100)
    orden_corte_id: Optional[int] = None  # Asociación con orden de corte
    remision_numero: Optional[str] = None
    confeccionista_nombre: Optional[str] = None
    fecha_entrega: Optional[datetime] = None
    fecha_entrega_estimada: Optional[datetime] = None
    despacha: Optional[bool] = None
    estado: Optional[EstadoLote] = None
    fecha_corte: Optional[datetime] = None
    fecha_asignacion: Optional[datetime] = None
    observaciones: Optional[str] = Field(None, max_length=500)
    es_pedido_especial: Optional[bool] = None
    prioridad: Optional[int] = Field(None, ge=0, le=2)
    cantidad_total_programada: Optional[int] = Field(None, ge=0)
    detalles: Optional[List[LoteDetalleCreate]] = None  # Permitir actualizar detalles

class LoteResponse(BaseModel):
    id: int
    numero_lote: str
    mesa: Optional[str] = None
    referencia_nombre: str  # Siempre mostrar el nombre
    material_nombre: str  # Siempre mostrar el nombre
    orden_corte_id: Optional[int] = None  # Asociación con orden de corte
    remision_numero: Optional[str] = None
    confeccionista_nombre: Optional[str] = None
    fecha_entrega: Optional[datetime] = None
    fecha_entrega_estimada: Optional[datetime] = None
    despacha: Optional[bool] = None
    estado: EstadoLote
    fecha_corte: datetime
    fecha_asignacion: Optional[datetime] = None
    observaciones: Optional[str] = None
    es_pedido_especial: bool = False
    prioridad: int = 0
    cantidad_total_programada: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    detalles: List[LoteDetalleResponse] = []
    
    @model_validator(mode='before')
    @classmethod
    def calcular_nombres(cls, data: Any) -> Any:
        """Calcula los nombres de referencia y material desde las relaciones"""
        # Si data es un objeto SQLAlchemy (tiene relaciones)
        if not isinstance(data, dict) and hasattr(data, '__dict__'):
            # Obtener nombres desde relaciones o atributos existentes
            referencia_nombre = None
            material_nombre = None
            
            # Intentar obtener nombres de atributos existentes
            if hasattr(data, 'referencia_nombre') and data.referencia_nombre:
                referencia_nombre = data.referencia_nombre
            elif 'referencia_nombre' in data.__dict__:
                referencia_nombre = data.__dict__.get('referencia_nombre')
            
            if hasattr(data, 'material_nombre') and data.material_nombre:
                material_nombre = data.material_nombre
            elif 'material_nombre' in data.__dict__:
                material_nombre = data.__dict__.get('material_nombre')
            
            # Si no están, obtenerlos de las relaciones
            if not referencia_nombre:
                if hasattr(data, 'referencia') and data.referencia:
                    try:
                        referencia_nombre = data.referencia.nombre or data.referencia.codigo or ''
                    except:
                        referencia_nombre = ''
                else:
                    referencia_nombre = ''
            
            if not material_nombre:
                if hasattr(data, 'material') and data.material:
                    try:
                        material_nombre = data.material.nombre or data.material.codigo or ''
                    except:
                        material_nombre = ''
                else:
                    material_nombre = ''
            
            # Construir diccionario manualmente con todos los campos necesarios
            from sqlalchemy.inspection import inspect
            mapper = inspect(data.__class__)
            result_dict = {}
            
            # Copiar todas las columnas del modelo
            for column in mapper.columns:
                value = getattr(data, column.key, None)
                # Incluir valores None para campos opcionales
                if value is not None:
                    result_dict[column.key] = value
                elif column.key in ['mesa', 'fecha_asignacion', 'observaciones', 'updated_at']:
                    result_dict[column.key] = None
            
            # Agregar detalles si existen
            if hasattr(data, 'detalles') and data.detalles:
                result_dict['detalles'] = list(data.detalles)
            else:
                result_dict['detalles'] = []
            
            # Asegurar que los nombres estén presentes (sobrescribir si ya existen)
            # Si están vacíos, intentar obtenerlos nuevamente
            if not referencia_nombre and hasattr(data, 'referencia') and data.referencia:
                referencia_nombre = data.referencia.nombre or data.referencia.codigo or 'Sin referencia'
            
            if not material_nombre and hasattr(data, 'material') and data.material:
                material_nombre = data.material.nombre or data.material.codigo or 'Sin material'
            
            result_dict['referencia_nombre'] = referencia_nombre if referencia_nombre else 'Sin referencia'
            result_dict['material_nombre'] = material_nombre if material_nombre else 'Sin material'
            
            return result_dict
        return data
    
    class Config:
        from_attributes = True

