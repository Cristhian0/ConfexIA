from app.schemas.catalogo import (
    TallaBase, TallaCreate, TallaUpdate, TallaResponse,
    ColorBase, ColorCreate, ColorUpdate, ColorResponse,
    MaterialBase, MaterialCreate, MaterialUpdate, MaterialResponse,
    ReferenciaBase, ReferenciaCreate, ReferenciaUpdate, ReferenciaResponse
)
from app.schemas.colilla import (
    ColillaBase, ColillaCreate, ColillaUpdate, ColillaResponse,
    ColillaListResponse, ColillaStatusUpdate, ColillaExportRequest, ColillaFirmaPDFRequest, ColillaImportar
)
from app.schemas.lote import (
    LoteDetalleBase, LoteDetalleCreate, LoteDetalleUpdate, LoteDetalleResponse,
    LoteBase, LoteCreate, LoteUpdate, LoteResponse
)
from app.schemas.taller import (
    TallerBase, TallerCreate, TallerUpdate, TallerResponse,
    RemisionDetalleBase, RemisionDetalleCreate, RemisionDetalleUpdate, RemisionDetalleResponse,
    RemisionBase, RemisionCreate, RemisionUpdate, RemisionResponse
)
from app.schemas.produccion import (
    AvanceProduccionBase, AvanceProduccionCreate, AvanceProduccionUpdate, AvanceProduccionResponse,
    FallaConfeccionBase, FallaConfeccionCreate, FallaConfeccionUpdate, FallaConfeccionResponse,
    ControlCalidadBase, ControlCalidadCreate, ControlCalidadUpdate, ControlCalidadResponse,
    ImperfectoCalidadBase, ImperfectoCalidadCreate, ImperfectoCalidadUpdate, ImperfectoCalidadResponse
)
from app.schemas.documentos import (
    NOCBase,
    NOCCreate,
    NOCResponse,
    AlmacenamientoZonaBase,
    AlmacenamientoZonaCreate,
    AlmacenamientoZonaResponse,
    FinancieroRegistroBase,
    FinancieroRegistroCreate,
    FinancieroRegistroResponse,
)

from app.schemas.bodega import (
    RolloStockResponse,
    RolloMovimientoResponse,
    IngresoRolloCreate,
    SalidaRolloCreate,
)
from app.schemas.producto_terminado import (
    ProductoTerminadoStockResponse,
    ProductoTerminadoStockCreate,
    ProductoTerminadoStockUpdate,
    ProductoTerminadoMovimientoResponse,
)

__all__ = [
    "TallaBase", "TallaCreate", "TallaUpdate", "TallaResponse",
    "ColorBase", "ColorCreate", "ColorUpdate", "ColorResponse",
    "MaterialBase", "MaterialCreate", "MaterialUpdate", "MaterialResponse",
    "ReferenciaBase", "ReferenciaCreate", "ReferenciaUpdate", "ReferenciaResponse",
    "ColillaBase", "ColillaCreate", "ColillaUpdate", "ColillaResponse",
    "ColillaListResponse", "ColillaStatusUpdate", "ColillaExportRequest", "ColillaFirmaPDFRequest", "ColillaImportar",
    "LoteDetalleBase", "LoteDetalleCreate", "LoteDetalleUpdate", "LoteDetalleResponse",
    "LoteBase", "LoteCreate", "LoteUpdate", "LoteResponse",
    "TallerBase", "TallerCreate", "TallerUpdate", "TallerResponse",
    "RemisionDetalleBase", "RemisionDetalleCreate", "RemisionDetalleUpdate", "RemisionDetalleResponse",
    "RemisionBase", "RemisionCreate", "RemisionUpdate", "RemisionResponse",
    "AvanceProduccionBase", "AvanceProduccionCreate", "AvanceProduccionUpdate", "AvanceProduccionResponse",
    "FallaConfeccionBase", "FallaConfeccionCreate", "FallaConfeccionUpdate", "FallaConfeccionResponse",
    "ControlCalidadBase", "ControlCalidadCreate", "ControlCalidadUpdate", "ControlCalidadResponse",
    "ImperfectoCalidadBase", "ImperfectoCalidadCreate", "ImperfectoCalidadUpdate", "ImperfectoCalidadResponse",
    "NOCBase", "NOCCreate", "NOCResponse",
    "AlmacenamientoZonaBase", "AlmacenamientoZonaCreate", "AlmacenamientoZonaResponse",
    "FinancieroRegistroBase", "FinancieroRegistroCreate", "FinancieroRegistroResponse",
    "RolloStockResponse", "RolloMovimientoResponse", "IngresoRolloCreate", "SalidaRolloCreate",
    "ProductoTerminadoStockResponse", "ProductoTerminadoStockCreate", "ProductoTerminadoStockUpdate", "ProductoTerminadoMovimientoResponse",
]

