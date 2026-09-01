from enum import Enum

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class EstadoOrdenCorte(str, Enum):
    BORRADOR = "borrador"
    TIZADO = "tizado"
    CORTADO = "cortado"
    CERRADA = "cerrada"


class OrdenCorte(Base):
    """RF-04: orden de corte con tallas/cantidades; RF-05 a RF-07 opcionales en mismos campos."""

    __tablename__ = "ordenes_corte"

    id = Column(Integer, primary_key=True, index=True)
    numero_orden = Column(String(50), unique=True, nullable=False, index=True)
    tipo_prenda = Column(String(120), nullable=False)
    estado = Column(
        SQLEnum(EstadoOrdenCorte),
        default=EstadoOrdenCorte.BORRADOR,
        nullable=False,
        server_default="borrador",
    )

    metros_tizado = Column(Numeric(12, 2), nullable=True)
    rendimiento_pct = Column(Numeric(5, 2), nullable=True)
    piezas_cortadas = Column(Integer, nullable=True)
    capas_utilizadas = Column(Integer, nullable=True)
    metros_sobrante = Column(Numeric(12, 2), nullable=True)
    metros_desperdicio = Column(Numeric(12, 2), nullable=True)
    observaciones = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    lineas = relationship(
        "OrdenCorteLinea", back_populates="orden", cascade="all, delete-orphan"
    )
    reservas = relationship("ReservaTela", back_populates="orden_corte")
    lotes = relationship("Lote", back_populates="orden_corte")


class OrdenCorteLinea(Base):
    __tablename__ = "orden_corte_lineas"

    id = Column(Integer, primary_key=True, index=True)
    orden_corte_id = Column(Integer, ForeignKey("ordenes_corte.id"), nullable=False, index=True)
    talla_codigo = Column(String(20), nullable=False)
    cantidad = Column(Integer, nullable=False, default=0)

    orden = relationship("OrdenCorte", back_populates="lineas")


class EstadoReservaTela(str, Enum):
    ACTIVA = "activa"
    CONSUMIDA = "consumida"
    CANCELADA = "cancelada"


class ReservaTela(Base):
    """RF-03: reservar metros de tela hacia una orden de corte."""

    __tablename__ = "reservas_tela"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materiales.id"), nullable=False, index=True)
    color_id = Column(Integer, ForeignKey("colores.id"), nullable=False, index=True)
    metros = Column(Numeric(12, 2), nullable=False)
    orden_corte_id = Column(Integer, ForeignKey("ordenes_corte.id"), nullable=True, index=True)
    estado = Column(
        SQLEnum(EstadoReservaTela),
        default=EstadoReservaTela.ACTIVA,
        nullable=False,
        server_default="activa",
    )
    observaciones = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    orden_corte = relationship("OrdenCorte", back_populates="reservas")
    material = relationship("Material")
    color = relationship("Color")
