export enum ZonaAlmacen {
  A1 = 'A1',
  A2 = 'A2',
  A3 = 'A3'
}

export enum TipoMovimientoFinanciero {
  ANTICIPO = 'anticipo',
  COSTO_PROCESO = 'costo_proceso'
}

export interface NOC {
  id: number;
  numero_noc: string;
  lote_id: number;
  remision_id: number;
  fecha_generacion: string;
  observaciones?: string;
}

export interface NOCCreate {
  numero_noc: string;
  lote_id: number;
  remision_id: number;
  observaciones?: string;
  fecha_generacion?: string;
}

export interface AlmacenamientoZona {
  id: number;
  noc_id: number;
  zona: ZonaAlmacen;
  almacenado_por?: string;
  fecha_asignacion: string;
}

export interface AlmacenamientoZonaCreate {
  noc_id: number;
  zona: ZonaAlmacen;
  almacenado_por?: string;
  fecha_asignacion?: string;
}

export interface FinancieroRegistro {
  id: number;
  noc_id: number;
  tipo: TipoMovimientoFinanciero;
  monto: number;
  descripcion?: string;
  fecha_registro: string;
}

export interface FinancieroRegistroCreate {
  noc_id: number;
  tipo: TipoMovimientoFinanciero;
  monto: number;
  descripcion?: string;
  fecha_registro?: string;
}

