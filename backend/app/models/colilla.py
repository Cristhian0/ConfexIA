from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from app.db.database import Base


class EstadoColilla(str, Enum):
    """Estados de una colilla de confección"""
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"


class TipoTrabajo(str, Enum):
    """Tipos de trabajo en confección"""
    ENSAMBLE = "ensamble"
    COSTURA = "costura"
    FILETEADO = "fileteado"
    TERMINACION = "terminacion"
    OTRO = "otro"


class Colilla(Base):
    """RF-XX: Colilla de confección para confeccionistas"""
    __tablename__ = "colillas"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_colilla = Column(String(50), unique=True, nullable=False, index=True)
    remision_detalle_id = Column(Integer, ForeignKey("remision_detalles.id"), nullable=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    taller_id = Column(Integer, ForeignKey("talleres.id"), nullable=False)
    
    # Datos del confeccionista
    confeccionista_nombre = Column(String(200), nullable=False)
    confeccionista_cedula = Column(String(20), nullable=True)
    
    # Información de trabajo
    tipo_trabajo = Column(SQLEnum(TipoTrabajo), nullable=False)
    cantidad_prendas = Column(Integer, nullable=False, default=0)
    descripcion_trabajo = Column(Text, nullable=True)
    referencia = Column(String(100), nullable=True)
    talla_id = Column(Integer, ForeignKey("tallas.id"), nullable=True)
    color = Column(String(100), nullable=True)
    
    # Control de cumplimiento
    cantidad_completada = Column(Integer, default=0)
    cantidad_rechazada = Column(Integer, default=0)
    
    # Estados y fechas
    estado = Column(SQLEnum(EstadoColilla), default=EstadoColilla.PENDIENTE, nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_asignacion = Column(DateTime(timezone=True), nullable=True)
    fecha_limite_entrega = Column(Date, nullable=True)
    fecha_completacion = Column(DateTime(timezone=True), nullable=True)
    
    # Observaciones
    observaciones = Column(Text, nullable=True)

    # Firma del confeccionista (imagen en base64)
    firma_base64 = Column(Text, nullable=True)
    
    # Metadata
    activa = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    lote = relationship("Lote")
    taller = relationship("Taller")
    remision_detalle = relationship("RemisionDetalle")
