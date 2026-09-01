from enum import Enum

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base
from app.models.documentos import ZonaAlmacen


class TipoMovimientoProductoTerminado(str, Enum):
    INGRESO = "ingreso"
    SALIDA = "salida"
    AJUSTE = "ajuste"


class ProductoTerminadoStock(Base):
    __tablename__ = "producto_terminado_stocks"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    tipo = Column(String(100), nullable=False)
    talla_id = Column(Integer, ForeignKey("tallas.id"), nullable=False)
    color_id = Column(Integer, ForeignKey("colores.id"), nullable=False)
    zona = Column(SQLEnum(ZonaAlmacen), nullable=False)
    cantidad_actual = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    movimientos = relationship("ProductoTerminadoMovimiento", cascade="all, delete-orphan")
    talla = relationship("Talla")
    color = relationship("Color")


class ProductoTerminadoMovimiento(Base):
    __tablename__ = "producto_terminado_movimientos"

    id = Column(Integer, primary_key=True, index=True)
    producto_stock_id = Column(Integer, ForeignKey("producto_terminado_stocks.id"), nullable=False, index=True)
    tipo = Column(SQLEnum(TipoMovimientoProductoTerminado), nullable=False, index=True)
    cantidad = Column(Integer, nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha_movimiento = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    stock = relationship("ProductoTerminadoStock", overlaps="movimientos")
