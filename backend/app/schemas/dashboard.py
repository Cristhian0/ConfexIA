from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal

class CostoPrendaResponse(BaseModel):
    noc_id: Optional[int]
    lote_id: int
    total_prendas: int
    costo_tela: Decimal
    costo_mano_obra: Decimal
    costo_insumos: Decimal
    costo_otros: Decimal
    costo_total: Decimal
    costo_unitario: Decimal

class RentabilidadLoteResponse(BaseModel):
    lote_id: int
    total_prendas: int
    anticipo_total: Decimal
    costo_total: Decimal
    rentabilidad: Decimal
    rentabilidad_pct: Optional[Decimal]
    costo_unitario_promedio: Decimal

class ProduccionDiaLineaResponse(BaseModel):
    fecha: str
    linea_produccion: Optional[str]
    cantidad_producida: int
    cantidad_rechazada: int
    eficiencia_hph: float

class EficienciaOperarioResponse(BaseModel):
    operario: str
    produccion_total: int
    horas_trabajadas: float
    piezas_por_hora: float

class IndicadoresResponse(BaseModel):
    desperdicio_tela_pct: float
    defectos_pct: float
    costo_unitario_promedio: float
    eficiencia_operarios: List[EficienciaOperarioResponse]
