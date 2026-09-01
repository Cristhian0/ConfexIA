from app.models.catalogo import (
    Talla, Color, Material, Referencia
)
from app.models.corte import (
    OrdenCorte,
    OrdenCorteLinea,
    ReservaTela,
    EstadoOrdenCorte,
    EstadoReservaTela,
)
from app.models.lote import Lote, LoteDetalle
from app.models.taller import Taller, Remision, RemisionDetalle
from app.models.produccion import AvanceProduccion, FallaConfeccion
from app.models.documentos import NOC, AlmacenamientoZona, FinancieroRegistro
from app.models.bodega import RolloStock, RolloMovimiento, TipoMovimientoRollo
from app.models.producto_terminado import (
    ProductoTerminadoStock,
    ProductoTerminadoMovimiento,
    TipoMovimientoProductoTerminado,
)
from app.models.colilla import Colilla, EstadoColilla, TipoTrabajo

__all__ = [
    "OrdenCorte",
    "OrdenCorteLinea",
    "ReservaTela",
    "EstadoOrdenCorte",
    "EstadoReservaTela",
    "Talla",
    "Color",
    "Material",
    "Referencia",
    "Lote",
    "LoteDetalle",
    "Taller",
    "Remision",
    "RemisionDetalle",
    "AvanceProduccion",
    "FallaConfeccion",
    "NOC",
    "AlmacenamientoZona",
    "FinancieroRegistro",
    "RolloStock",
    "RolloMovimiento",
    "TipoMovimientoRollo",
    "ProductoTerminadoStock",
    "ProductoTerminadoMovimiento",
    "TipoMovimientoProductoTerminado",
    "Colilla",
    "EstadoColilla",
    "TipoTrabajo",
]

