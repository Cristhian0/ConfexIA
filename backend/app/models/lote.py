from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from app.db.database import Base

class EstadoLote(str, Enum):
    EN_CORTE = "en_corte"
    CORTE_COMPLETADO = "corte_completado"
    EN_CAMINO = "en_camino"
    EN_TALLER = "en_taller"
    EN_CONFECCION = "en_confeccion"
    PARCIALMENTE_ENTREGADO = "parcialmente_entregado"
    COMPLETADO = "completado"
    CANCELADO = "cancelado"

class Lote(Base):
    __tablename__ = "lotes"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_lote = Column(String(50), unique=True, nullable=False, index=True)
    mesa = Column(String(50), nullable=True)  # Mesa de corte
    referencia_id = Column(Integer, ForeignKey("referencias.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materiales.id"), nullable=False)
    orden_corte_id = Column(Integer, ForeignKey("ordenes_corte.id"), nullable=True, index=True)
    remision_numero = Column(String(200), nullable=True)
    confeccionista_nombre = Column(String(200), nullable=True)
    fecha_entrega = Column(DateTime(timezone=True), nullable=True)
    fecha_entrega_estimada = Column(DateTime(timezone=True), nullable=True)
    despacha = Column(Boolean, default=False, nullable=True)
    estado = Column(SQLEnum(EstadoLote), default=EstadoLote.EN_CORTE, nullable=False, server_default='en_corte')
    fecha_corte = Column(DateTime(timezone=True), nullable=False)
    fecha_asignacion = Column(DateTime(timezone=True), nullable=True)
    observaciones = Column(String(500), nullable=True)
    es_pedido_especial = Column(Boolean, default=False, nullable=False)
    prioridad = Column(Integer, default=0)  # 0=normal, 1=alta, 2=urgente
    cantidad_total_programada = Column(Integer, default=0)  # Total programado por referencia
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    referencia = relationship("Referencia", back_populates="lotes")
    material = relationship("Material", back_populates="lotes")
    detalles = relationship("LoteDetalle", back_populates="lote", cascade="all, delete-orphan")
    orden_corte = relationship("OrdenCorte", back_populates="lotes")
    remisiones = relationship("Remision", back_populates="lote")
    avances = relationship("AvanceProduccion", back_populates="lote")
    fallas = relationship("FallaConfeccion", back_populates="lote")
    controles_calidad = relationship("ControlCalidad", back_populates="lote")

class LoteDetalle(Base):
    __tablename__ = "lote_detalles"
    
    id = Column(Integer, primary_key=True, index=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    color_nombre = Column(String(100), nullable=True)  # Nombre del color almacenado directamente (nullable para migración)
    talla_id = Column(Integer, ForeignKey("tallas.id"), nullable=False)
    cantidad = Column(Integer, nullable=False, default=0)  # Cantidad programada por color y talla
    cantidad_cortada = Column(Integer, default=0)
    cantidad_en_taller = Column(Integer, default=0)
    cantidad_confeccionada = Column(Integer, default=0)
    cantidad_entregada = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    lote = relationship("Lote", back_populates="detalles")
    talla = relationship("Talla", back_populates="lote_detalles")

