from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from app.db.database import Base


class ZonaAlmacen(str, Enum):
    A1 = "A1"
    A2 = "A2"
    A3 = "A3"


class TipoMovimientoFinanciero(str, Enum):
    ANTICIPO = "anticipo"
    COSTO_PROCESO = "costo_proceso"


class NOC(Base):
    __tablename__ = "nocs"

    id = Column(Integer, primary_key=True, index=True)
    numero_noc = Column(String(50), unique=True, nullable=False, index=True)

    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False, index=True)
    remision_id = Column(Integer, ForeignKey("remisiones.id"), nullable=False, index=True)

    fecha_generacion = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    observaciones = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    almacenamientos = relationship("AlmacenamientoZona", cascade="all, delete-orphan")
    movimientos_financieros = relationship("FinancieroRegistro", cascade="all, delete-orphan")


class AlmacenamientoZona(Base):
    __tablename__ = "almacenamiento_zonas"

    id = Column(Integer, primary_key=True, index=True)
    noc_id = Column(Integer, ForeignKey("nocs.id"), nullable=False, unique=True, index=True)

    zona = Column(SQLEnum(ZonaAlmacen), nullable=False)
    almacenado_por = Column(String(200), nullable=True)
    fecha_asignacion = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    noc = relationship("NOC", overlaps="almacenamientos")


class FinancieroRegistro(Base):
    __tablename__ = "financiero_registros"

    id = Column(Integer, primary_key=True, index=True)
    noc_id = Column(Integer, ForeignKey("nocs.id"), nullable=False, index=True)

    tipo = Column(SQLEnum(TipoMovimientoFinanciero), nullable=False, index=True)
    monto = Column(Numeric(12, 2), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha_registro = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    noc = relationship("NOC", overlaps="movimientos_financieros")

