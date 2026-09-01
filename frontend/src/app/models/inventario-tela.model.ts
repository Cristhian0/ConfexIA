export enum TipoMovimientoRollo {
  INGRESO = 'ingreso',
  SALIDA = 'salida',
  AJUSTE = 'ajuste'
}

export interface RolloStock {
  id: number;
  material_id: number;
  color_id: number;
  lote_proveedor?: string;
  cantidad_actual: number;
  cantidad_reservada: number; // RF-03: tela reservada para producción
  material_nombre?: string;
  color_nombre?: string;
  created_at: string;
  updated_at?: string;
}

export interface IngresoRolloCreate {
  material_id: number;
  color_id: number;
  lote_proveedor: string;
  cantidad: number;
  orden_corte_id?: number;
  descripcion?: string;
}

export interface SalidaRolloCreate {
  material_id: number;
  color_id: number;
  cantidad: number;
  orden_corte_id?: number;
  descripcion?: string;
}

export interface RolloMovimiento {
  id: number;
  rollo_stock_id: number;
  tipo: TipoMovimientoRollo;
  cantidad: number;
  orden_corte_id?: number;
  descripcion?: string;
  fecha_movimiento: string;
}

