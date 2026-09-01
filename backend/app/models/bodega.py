from enum import Enum

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class TipoMovimientoRollo(str, Enum):
    INGRESO = "ingreso"
    SALIDA = "salida"
    AJUSTE = "ajuste"


class RolloStock(Base):
    __tablename__ = "rollo_stocks"

    id = Column(Integer, primary_key=True, index=True)

    material_id = Column(Integer, ForeignKey("materiales.id"), nullable=False)
    color_id = Column(Integer, ForeignKey("colores.id"), nullable=False)
    lote_proveedor = Column(String(50), nullable=True)  # Lote del proveedor

    cantidad_actual = Column(Numeric(12, 2), nullable=False, default=0)
    cantidad_reservada = Column(Numeric(12, 2), nullable=False, default=0)  # RF-03: tela reservada para producción

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    movimientos = relationship("RolloMovimiento", cascade="all, delete-orphan")

    material = relationship("Material")
    color = relationship("Color")

    __table_args__ = (UniqueConstraint("material_id", "color_id", "lote_proveedor", name="uix_rollo_stock_material_color_lote"),)


class RolloMovimiento(Base):
    __tablename__ = "rollo_movimientos"

    id = Column(Integer, primary_key=True, index=True)

    rollo_stock_id = Column(Integer, ForeignKey("rollo_stocks.id"), nullable=False, index=True)

    tipo = Column(SQLEnum(TipoMovimientoRollo), nullable=False, index=True)
    cantidad = Column(Numeric(12, 2), nullable=False)

    # Para trazabilidad con "orden de corte"
    orden_corte_id = Column(Integer, nullable=True, index=True)
    descripcion = Column(Text, nullable=True)

    fecha_movimiento = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    stock = relationship("RolloStock", overlaps="movimientos")

