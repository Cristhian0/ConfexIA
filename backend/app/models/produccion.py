from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from app.db.database import Base

class TipoOperacion(str, Enum):
    ENSAMBLE = "ensamble"
    COSTURA = "costura"
    FILETEADO = "fileteado"
    TERMINACION = "terminacion"

class EstadoOrdenProduccion(str, Enum):
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"

class OrdenProduccion(Base):
    """RF-11: Orden de confección asociada a un lote"""
    __tablename__ = "ordenes_produccion"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_orden = Column(String(50), unique=True, nullable=False, index=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    estado = Column(SQLEnum(EstadoOrdenProduccion), default=EstadoOrdenProduccion.PENDIENTE, nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_inicio = Column(DateTime(timezone=True), nullable=True)
    fecha_fin = Column(DateTime(timezone=True), nullable=True)
    observaciones = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    lote = relationship("Lote")
    registros_produccion = relationship("RegistroProduccion", back_populates="orden_produccion", cascade="all, delete-orphan")

class RegistroProduccion(Base):
    """RF-12, RF-13, RF-14: Registro de producción por operación"""
    __tablename__ = "registros_produccion"
    
    id = Column(Integer, primary_key=True, index=True)
    orden_produccion_id = Column(Integer, ForeignKey("ordenes_produccion.id"), nullable=False)
    operacion = Column(SQLEnum(TipoOperacion), nullable=False)  # Ensamble, Costura, Fileteado, Terminación
    operario = Column(String(200), nullable=False)  # Nombre del operario
    linea_produccion = Column(String(50), nullable=True)  # Identificación de línea (A1, A2, etc)
    cantidad_producida = Column(Integer, default=0)  # Cantidad de piezas procesadas
    cantidad_rechazada = Column(Integer, default=0)  # Cantidad de piezas defectuosas
    tiempo_inicio = Column(DateTime(timezone=True), nullable=False)  # RF-14: Hora de inicio
    tiempo_fin = Column(DateTime(timezone=True), nullable=True)  # RF-14: Hora de fin
    tiempo_total_minutos = Column(Integer, nullable=True)  # Calculado: fin - inicio
    notas = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    orden_produccion = relationship("OrdenProduccion", back_populates="registros_produccion")

class AvanceProduccion(Base):
    __tablename__ = "avances_produccion"
    
    id = Column(Integer, primary_key=True, index=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    taller_id = Column(Integer, ForeignKey("talleres.id"), nullable=False)
    remision_id = Column(Integer, ForeignKey("remisiones.id"), nullable=True)
    fecha_avance = Column(DateTime(timezone=True), nullable=False)
    operacion = Column(SQLEnum(TipoOperacion), nullable=True)
    cantidad_avance = Column(Integer, nullable=False, default=0)
    porcentaje_avance = Column(Integer, nullable=False, default=0)  # 0-100
    observaciones = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    lote = relationship("Lote", back_populates="avances")
    taller = relationship("Taller", back_populates="avances")
    remision = relationship("Remision")

class TipoFalla(str, Enum):
    DEFECTO_TELA = "defecto_tela"
    DEFECTO_CONFECCION = "defecto_confeccion"
    DEFECTO_COLOR = "defecto_color"
    DEFECTO_TALLA = "defecto_talla"
    OTRO = "otro"

class EstadoFalla(str, Enum):
    REPORTADA = "reportada"
    EN_REVISION = "en_revision"
    CORREGIDA = "corregida"
    RECHAZADA = "rechazada"

class EstadoControlCalidad(str, Enum):
    PENDIENTE_INSPECCION = "pendiente_inspeccion"
    EN_INSPECCION = "en_inspeccion"
    APROBADO = "aprobado"
    CON_IMPERFECCIONES = "con_imperfecciones"
    DEVUELTO_TALLER = "devuelto_taller"
    EN_REPARACION = "en_reparacion"
    REPARADO = "reparado"
    RECHAZADO = "rechazado"

class TipoImperfecto(str, Enum):
    DEFECTO_TELA = "defecto_tela"
    DEFECTO_CONFECCION = "defecto_confeccion"
    DEFECTO_COLOR = "defecto_color"
    DEFECTO_TALLA = "defecto_talla"
    MEDIDAS_INCORRECTAS = "medidas_incorrectas"
    ACABADO_DEFICIENTE = "acabado_deficiente"
    OTRO = "otro"

class ControlCalidad(Base):
    __tablename__ = "controles_calidad"
    
    id = Column(Integer, primary_key=True, index=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    remision_id = Column(Integer, ForeignKey("remisiones.id"), nullable=False)
    fecha_inspeccion = Column(DateTime(timezone=True), nullable=False)
    inspector = Column(String(200), nullable=False)
    estado = Column(SQLEnum(EstadoControlCalidad), default=EstadoControlCalidad.PENDIENTE_INSPECCION, nullable=False)
    
    # Cantidades
    cantidad_recibida = Column(Integer, nullable=False, default=0)
    cantidad_aprobada = Column(Integer, default=0)
    cantidad_imperfecciones = Column(Integer, default=0)
    cantidad_pendiente_confeccion = Column(Integer, default=0)
    cantidad_devuelta = Column(Integer, default=0)
    
    observaciones_generales = Column(Text, nullable=True)
    fecha_devolucion = Column(DateTime(timezone=True), nullable=True)
    fecha_recepcion_reparado = Column(DateTime(timezone=True), nullable=True)
    # Campos adicionales solicitados
    fecha_recepcion = Column(DateTime(timezone=True), nullable=True)
    revisado_por = Column(String(200), nullable=True)
    cantidad_parcial = Column(Integer, default=0)
    cantidad_arreglos = Column(Integer, default=0)
    tiene_imperfecciones = Column(Boolean, default=False)
    cantidad_pendiente = Column(Integer, default=0)
    requiere_compras = Column(Boolean, default=False)
    fecha_entrega_total = Column(DateTime(timezone=True), nullable=True)
    dias_mora = Column(Integer, default=0)
    estado_pago = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    lote = relationship("Lote", back_populates="controles_calidad")
    remision = relationship("Remision", back_populates="controles_calidad")
    imperfectos = relationship("ImperfectoCalidad", back_populates="control_calidad", cascade="all, delete-orphan")

class ImperfectoCalidad(Base):
    __tablename__ = "imperfectos_calidad"
    
    id = Column(Integer, primary_key=True, index=True)
    control_calidad_id = Column(Integer, ForeignKey("controles_calidad.id"), nullable=False)
    tipo_imperfecto = Column(SQLEnum(TipoImperfecto), nullable=False)
    cantidad_afectada = Column(Integer, nullable=False, default=0)
    descripcion = Column(Text, nullable=False)
    causa = Column(Text, nullable=True)
    arreglo_requerido = Column(Text, nullable=True)
    estado_arreglo = Column(SQLEnum(EstadoControlCalidad), default=EstadoControlCalidad.CON_IMPERFECCIONES, nullable=False)
    fecha_reporte = Column(DateTime(timezone=True), server_default=func.now())
    fecha_arreglo = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    control_calidad = relationship("ControlCalidad", back_populates="imperfectos")

class FallaConfeccion(Base):
    __tablename__ = "fallas_confeccion"
    
    id = Column(Integer, primary_key=True, index=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    remision_id = Column(Integer, ForeignKey("remisiones.id"), nullable=True)
    taller_id = Column(Integer, ForeignKey("talleres.id"), nullable=True)
    tipo_falla = Column(SQLEnum(TipoFalla), nullable=False)
    estado = Column(SQLEnum(EstadoFalla), default=EstadoFalla.REPORTADA, nullable=False)
    cantidad_afectada = Column(Integer, nullable=False, default=0)
    descripcion = Column(Text, nullable=False)
    accion_correctiva = Column(Text, nullable=True)
    fecha_reporte = Column(DateTime(timezone=True), nullable=False)
    fecha_resolucion = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    lote = relationship("Lote", back_populates="fallas")
    taller = relationship("Taller")
    remision = relationship("Remision")


# ========== MÓDULO 5: CONTROL DE CALIDAD ==========

class TipoDefecto(str, Enum):
    """RF-17: Tipos de defectos encontrados"""
    COSTURA = "costura"
    MEDIDA = "medida"
    MANCHA = "mancha"
    TELA = "tela"

class ClasificacionInspeccion(str, Enum):
    """RF-16: Clasificación de prendas inspeccionadas"""
    OK = "ok"
    REPROCESO = "reproceso"
    DEFECTUOSA = "defectuosa"

class InspeccionCalidad(Base):
    """RF-15: Inspección de prendas del Módulo 5"""
    __tablename__ = "inspecciones_calidad"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_inspeccion = Column(String(50), unique=True, nullable=False, index=True)
    orden_produccion_id = Column(Integer, ForeignKey("ordenes_produccion.id"), nullable=False)
    inspector = Column(String(200), nullable=False)  # Nombre del inspector
    clasificacion = Column(SQLEnum(ClasificacionInspeccion), nullable=False)  # RF-16: OK, Reproceso, Defectuosa
    cantidad_inspeccionada = Column(Integer, default=0)
    cantidad_ok = Column(Integer, default=0)
    cantidad_reproceso = Column(Integer, default=0)
    cantidad_defectuosa = Column(Integer, default=0)
    observaciones = Column(Text, nullable=True)
    reingresar_produccion = Column(Boolean, default=False)  # RF-18: Si aplica reinicio a producción
    fecha_inspeccion = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    orden_produccion = relationship("OrdenProduccion")
    defectos = relationship("DefectoInspeccion", back_populates="inspeccion", cascade="all, delete-orphan")

class DefectoInspeccion(Base):
    """RF-17: Defectos encontrados durante inspección"""
    __tablename__ = "defectos_inspeccion"
    
    id = Column(Integer, primary_key=True, index=True)
    inspeccion_id = Column(Integer, ForeignKey("inspecciones_calidad.id"), nullable=False)
    tipo_defecto = Column(SQLEnum(TipoDefecto), nullable=False)  # RF-17: Costura, Medida, Mancha, Tela
    cantidad_defectos = Column(Integer, default=0)
    descripcion = Column(Text, nullable=True)
    recomendacion = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    inspeccion = relationship("InspeccionCalidad", back_populates="defectos")

