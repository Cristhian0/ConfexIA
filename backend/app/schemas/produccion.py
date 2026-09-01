from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any, Union
from datetime import datetime, date
from app.models.produccion import TipoFalla, EstadoFalla, EstadoControlCalidad, TipoImperfecto, TipoOperacion, EstadoOrdenProduccion
from app.schemas.lote import LoteResponse
from app.schemas.taller import RemisionResponse

# ========== RF-11: OrdenProduccion Schemas ==========
class OrdenProduccionBase(BaseModel):
    lote_id: int
    observaciones: Optional[str] = None

class OrdenProduccionCreate(OrdenProduccionBase):
    pass

class OrdenProduccionUpdate(BaseModel):
    estado: Optional[EstadoOrdenProduccion] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    observaciones: Optional[str] = None

class OrdenProduccionResponse(OrdenProduccionBase):
    id: int
    numero_orden: str
    estado: EstadoOrdenProduccion
    fecha_creacion: datetime
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ========== RF-12, RF-13, RF-14: RegistroProduccion Schemas ==========
class RegistroProduccionBase(BaseModel):
    orden_produccion_id: int
    operacion: TipoOperacion  # Ensamble, Costura, Fileteado, Terminación
    operario: str = Field(..., max_length=200)
    linea_produccion: Optional[str] = Field(None, max_length=50)
    cantidad_producida: int = Field(default=0, ge=0)
    cantidad_rechazada: int = Field(default=0, ge=0)
    tiempo_inicio: datetime
    tiempo_fin: Optional[datetime] = None
    notas: Optional[str] = None

class RegistroProduccionCreate(RegistroProduccionBase):
    pass

class RegistroProduccionUpdate(BaseModel):
    operario: Optional[str] = Field(None, max_length=200)
    linea_produccion: Optional[str] = Field(None, max_length=50)
    cantidad_producida: Optional[int] = Field(None, ge=0)
    cantidad_rechazada: Optional[int] = Field(None, ge=0)
    tiempo_fin: Optional[datetime] = None
    notas: Optional[str] = None

class RegistroProduccionResponse(RegistroProduccionBase):
    id: int
    tiempo_total_minutos: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# AvanceProduccion Schemas
class AvanceProduccionBase(BaseModel):
    lote_id: int
    taller_id: int
    remision_id: Optional[int] = None
    fecha_avance: datetime
    operacion: Optional[TipoOperacion] = None
    cantidad_avance: int = Field(..., ge=0)
    porcentaje_avance: int = Field(..., ge=0, le=100)
    observaciones: Optional[str] = None

class AvanceProduccionCreate(AvanceProduccionBase):
    pass

class AvanceProduccionUpdate(BaseModel):
    lote_id: Optional[int] = None
    taller_id: Optional[int] = None
    remision_id: Optional[int] = None
    fecha_avance: Optional[datetime] = None
    operacion: Optional[TipoOperacion] = None
    cantidad_avance: Optional[int] = Field(None, ge=0)
    porcentaje_avance: Optional[int] = Field(None, ge=0, le=100)
    observaciones: Optional[str] = None

class AvanceProduccionResponse(AvanceProduccionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# FallaConfeccion Schemas
class FallaConfeccionBase(BaseModel):
    lote_id: int
    remision_id: Optional[int] = None
    taller_id: Optional[int] = None
    tipo_falla: TipoFalla
    cantidad_afectada: int = Field(..., ge=0)
    descripcion: str
    fecha_reporte: datetime

class FallaConfeccionCreate(FallaConfeccionBase):
    pass

class FallaConfeccionUpdate(BaseModel):
    lote_id: Optional[int] = None
    remision_id: Optional[int] = None
    taller_id: Optional[int] = None
    tipo_falla: Optional[TipoFalla] = None
    estado: Optional[EstadoFalla] = None
    cantidad_afectada: Optional[int] = Field(None, ge=0)
    descripcion: Optional[str] = None
    accion_correctiva: Optional[str] = None
    fecha_reporte: Optional[datetime] = None
    fecha_resolucion: Optional[datetime] = None

class FallaConfeccionResponse(FallaConfeccionBase):
    id: int
    estado: EstadoFalla
    accion_correctiva: Optional[str] = None
    fecha_resolucion: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ControlCalidad Schemas
class ImperfectoCalidadBase(BaseModel):
    tipo_imperfecto: TipoImperfecto
    cantidad_afectada: int = Field(..., ge=0)
    descripcion: str
    causa: Optional[str] = None
    arreglo_requerido: Optional[str] = None

class ImperfectoCalidadCreate(ImperfectoCalidadBase):
    pass

class ImperfectoCalidadUpdate(BaseModel):
    tipo_imperfecto: Optional[TipoImperfecto] = None
    cantidad_afectada: Optional[int] = Field(None, ge=0)
    descripcion: Optional[str] = None
    causa: Optional[str] = None
    arreglo_requerido: Optional[str] = None
    estado_arreglo: Optional[EstadoControlCalidad] = None
    fecha_arreglo: Optional[datetime] = None

class ImperfectoCalidadResponse(ImperfectoCalidadBase):
    id: int
    control_calidad_id: int
    estado_arreglo: EstadoControlCalidad
    fecha_reporte: datetime
    fecha_arreglo: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ControlCalidadBase(BaseModel):
    lote_id: int
    remision_id: int
    fecha_inspeccion: Union[datetime, str] = Field(...)
    inspector: str = Field(..., max_length=200)
    cantidad_recibida: int = Field(..., ge=0)
    cantidad_aprobada: int = Field(0, ge=0)
    cantidad_imperfecciones: int = Field(0, ge=0)
    cantidad_pendiente_confeccion: int = Field(0, ge=0)
    cantidad_devuelta: int = Field(0, ge=0)
    # Nuevos campos de calidad
    fecha_recepcion: Optional[datetime] = None
    revisado_por: Optional[str] = None
    cantidad_parcial: int = Field(0, ge=0)
    cantidad_arreglos: int = Field(0, ge=0)
    tiene_imperfecciones: bool = Field(False)
    cantidad_pendiente: int = Field(0, ge=0)
    requiere_compras: bool = Field(False)
    fecha_entrega_total: Optional[datetime] = None
    dias_mora: int = Field(0, ge=0)
    estado_pago: Optional[str] = None
    observaciones_generales: Optional[str] = None

    @field_validator('fecha_inspeccion', mode='before')
    @classmethod
    def parse_fecha_inspeccion(cls, v):
        if isinstance(v, str):
            try:
                # Intenta parsear como datetime completo
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # Si no funciona, intenta como fecha simple (YYYY-MM-DD)
                    return datetime.combine(datetime.strptime(v, '%Y-%m-%d').date(), datetime.min.time())
                except ValueError:
                    raise ValueError(f'Formato de fecha inválido: {v}')
        return v

class ControlCalidadCreate(ControlCalidadBase):
    imperfectos: List[ImperfectoCalidadCreate] = []

class ControlCalidadUpdate(BaseModel):
    lote_id: Optional[int] = None
    remision_id: Optional[int] = None
    fecha_inspeccion: Optional[datetime] = None
    inspector: Optional[str] = Field(None, max_length=200)
    estado: Optional[EstadoControlCalidad] = None
    cantidad_recibida: Optional[int] = Field(None, ge=0)
    cantidad_aprobada: Optional[int] = Field(None, ge=0)
    cantidad_imperfecciones: Optional[int] = Field(None, ge=0)
    cantidad_pendiente_confeccion: Optional[int] = Field(None, ge=0)
    cantidad_devuelta: Optional[int] = Field(None, ge=0)
    # Campos editables nuevos
    fecha_recepcion: Optional[datetime] = None
    revisado_por: Optional[str] = None
    cantidad_parcial: Optional[int] = Field(None, ge=0)
    cantidad_arreglos: Optional[int] = Field(None, ge=0)
    tiene_imperfecciones: Optional[bool] = None
    cantidad_pendiente: Optional[int] = Field(None, ge=0)
    requiere_compras: Optional[bool] = None
    fecha_entrega_total: Optional[datetime] = None
    dias_mora: Optional[int] = Field(None, ge=0)
    estado_pago: Optional[str] = None
    observaciones_generales: Optional[str] = None
    fecha_devolucion: Optional[datetime] = None
    fecha_recepcion_reparado: Optional[datetime] = None

class ControlCalidadResponse(ControlCalidadBase):
    id: int
    estado: EstadoControlCalidad
    fecha_devolucion: Optional[datetime] = None
    fecha_recepcion_reparado: Optional[datetime] = None
    # Respuesta incluye los nuevos campos
    fecha_recepcion: Optional[datetime] = None
    revisado_por: Optional[str] = None
    cantidad_parcial: int = 0
    cantidad_arreglos: int = 0
    tiene_imperfecciones: bool = False
    cantidad_pendiente: int = 0
    requiere_compras: bool = False
    fecha_entrega_total: Optional[datetime] = None
    dias_mora: int = 0
    estado_pago: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    imperfectos: List[ImperfectoCalidadResponse] = []
    # Relaciones opcionales (solo si están cargadas con joinedload)
    lote: Optional[LoteResponse] = None
    remision: Optional[RemisionResponse] = None
    
    class Config:
        from_attributes = True


# ========== RF-15 a RF-18: InspeccionCalidad Schemas ==========
class DefectoInspeccionBase(BaseModel):
    tipo_defecto: str  # RF-17: Costura, Medida, Mancha, Tela
    cantidad_defectos: int = Field(default=0, ge=0)
    descripcion: Optional[str] = None
    recomendacion: Optional[str] = None

class DefectoInspeccionCreate(DefectoInspeccionBase):
    pass

class DefectoInspeccionResponse(DefectoInspeccionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class InspeccionCalidadBase(BaseModel):
    orden_produccion_id: int
    inspector: str = Field(..., max_length=200)
    clasificacion: str  # RF-16: OK, Reproceso, Defectuosa
    cantidad_inspeccionada: int = Field(default=0, ge=0)
    cantidad_ok: int = Field(default=0, ge=0)
    cantidad_reproceso: int = Field(default=0, ge=0)
    cantidad_defectuosa: int = Field(default=0, ge=0)
    observaciones: Optional[str] = None
    reingresar_produccion: bool = Field(default=False)  # RF-18: Si aplica reinicio

class InspeccionCalidadCreate(InspeccionCalidadBase):
    pass

class InspeccionCalidadUpdate(BaseModel):
    clasificacion: Optional[str] = None
    cantidad_ok: Optional[int] = None
    cantidad_reproceso: Optional[int] = None
    cantidad_defectuosa: Optional[int] = None
    observaciones: Optional[str] = None
    reingresar_produccion: Optional[bool] = None

class InspeccionCalidadResponse(InspeccionCalidadBase):
    id: int
    numero_inspeccion: str
    fecha_inspeccion: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    defectos: List[DefectoInspeccionResponse] = []
    
    class Config:
        from_attributes = True

