export enum ZonaAlmacen {
  A1 = 'A1',
  A2 = 'A2',
  A3 = 'A3'
}

export enum TipoMovimientoProductoTerminado {
  INGRESO = 'ingreso',
  SALIDA = 'salida',
  AJUSTE = 'ajuste'
}

export interface ProductoTerminadoStock {
  id: number;
  sku: string;
  tipo: string;
  talla_id: number;
  color_id: number;
  zona: ZonaAlmacen;
  cantidad_actual: number;
  talla_nombre?: string;
  color_nombre?: string;
  created_at: string;
  updated_at?: string;
}

export interface ProductoTerminadoStockCreate {
  sku: string;
  tipo: string;
  talla_id: number;
  color_id: number;
  zona: ZonaAlmacen;
  cantidad_actual: number;
  descripcion?: string;
}

export interface ProductoTerminadoStockUpdate {
  zona?: ZonaAlmacen;
  cantidad_actual?: number;
}

export interface ProductoTerminadoSalidaCreate {
  cantidad: number;
  descripcion?: string;
}

export interface ProductoTerminadoMovimiento {
  id: number;
  producto_stock_id: number;
  tipo: TipoMovimientoProductoTerminado;
  cantidad: number;
  descripcion?: string;
  fecha_movimiento: string;
}
