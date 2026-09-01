from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from app.db.database import Base

class Taller(Base):
    __tablename__ = "talleres"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, nullable=False, index=True)
    nombre = Column(String(200), nullable=False)
    direccion = Column(String(500), nullable=True)
    telefono = Column(String(20), nullable=True)
    contacto = Column(String(200), nullable=True)
    activo = Column(Boolean, default=True)
    capacidad_diaria = Column(Integer, default=0)  # Prendas por día
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    remisiones = relationship("Remision", back_populates="taller")
    avances = relationship("AvanceProduccion", back_populates="taller")

class EstadoRemision(str, Enum):
    PENDIENTE = "pendiente"
    EN_TRANSITO = "en_transito"
    RECIBIDA = "recibida"
    PARCIALMENTE_ENTREGADA = "parcialmente_entregada"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"

class Remision(Base):
    __tablename__ = "remisiones"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_remision = Column(String(50), unique=True, nullable=False, index=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    taller_id = Column(Integer, ForeignKey("talleres.id"), nullable=False)
    fecha_remision = Column(DateTime(timezone=True), nullable=False)
    fecha_entrega_estimada = Column(DateTime(timezone=True), nullable=True)
    fecha_recepcion = Column(DateTime(timezone=True), nullable=True)
    revisado_por = Column(String(200), nullable=True)  # Persona que recibió la remisión
    estado = Column(SQLEnum(EstadoRemision), default=EstadoRemision.PENDIENTE, nullable=False)
    observaciones = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    lote = relationship("Lote", back_populates="remisiones")
    taller = relationship("Taller", back_populates="remisiones")
    detalles = relationship("RemisionDetalle", back_populates="remision", cascade="all, delete-orphan")
    controles_calidad = relationship("ControlCalidad", back_populates="remision")

class RemisionDetalle(Base):
    __tablename__ = "remision_detalles"
    
    id = Column(Integer, primary_key=True, index=True)
    remision_id = Column(Integer, ForeignKey("remisiones.id"), nullable=False)
    talla_id = Column(Integer, ForeignKey("tallas.id"), nullable=False)
    cantidad = Column(Integer, nullable=False, default=0)
    cantidad_recibida = Column(Integer, default=0)
    cantidad_entregada = Column(Integer, default=0)
    # Datos del confeccionista / asignación
    confeccionista_nombre = Column(String(200), nullable=True)
    tipo_prenda = Column(String(200), nullable=True)
    fecha_entrega_estimada = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    remision = relationship("Remision", back_populates="detalles")
    talla = relationship("Talla")

