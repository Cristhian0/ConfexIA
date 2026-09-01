export enum EstadoLote {
  EN_CORTE = 'en_corte',
  CORTE_COMPLETADO = 'corte_completado',
  EN_CAMINO = 'en_camino',
  EN_TALLER = 'en_taller',
  EN_CONFECCION = 'en_confeccion',
  PARCIALMENTE_ENTREGADO = 'parcialmente_entregado',
  COMPLETADO = 'completado',
  CANCELADO = 'cancelado'
}

export interface LoteDetalle {
  id: number;
  lote_id: number;
  color_nombre?: string;  // Opcional para compatibilidad con datos antiguos
  talla_id: number;
  cantidad: number;
  cantidad_cortada: number;
  cantidad_en_taller: number;
  cantidad_confeccionada: number;
  cantidad_entregada: number;
  created_at: string;
  updated_at?: string;
}

export interface LoteDetalleCreate {
  color_nombre: string;
  talla_id: number;
  cantidad: number;
}

export interface Lote {
  id: number;
  numero_lote: string;
  mesa?: string;
  referencia_nombre: string;  // Nombre de la referencia
  material_nombre: string;  // Nombre del material
  orden_corte_id?: number;  // Asociación con orden de corte
  remision_numero?: string;
  confeccionista_nombre?: string;
  estado: EstadoLote;
  fecha_corte: string;
  fecha_entrega?: string;
  fecha_entrega_estimada?: string;
  despacha?: boolean;
  fecha_asignacion?: string;
  observaciones?: string;
  es_pedido_especial: boolean;
  prioridad: number;
  cantidad_total_programada?: number;
  created_at: string;
  updated_at?: string;
  detalles: LoteDetalle[];
  // Campos legacy para compatibilidad
  referencia_id?: number;
  material_id?: number;
}

export interface LoteCreate {
  numero_lote: string;
  mesa?: string;
  referencia_nombre: string;  // Nombre de la referencia
  material_nombre: string;  // Nombre del material
  orden_corte_id?: number;  // Asociación con orden de corte
  remision_numero?: string;
  confeccionista_nombre?: string;
  fecha_entrega?: string;
  fecha_entrega_estimada?: string;
  despacha?: boolean;
  fecha_corte: string;
  observaciones?: string;
  es_pedido_especial?: boolean;
  prioridad?: number;
  cantidad_total_programada?: number;
  detalles: LoteDetalleCreate[];
}

export interface LoteUpdate {
  numero_lote?: string;
  mesa?: string;
  referencia_nombre?: string;
  material_nombre?: string;
  orden_corte_id?: number;  // Asociación con orden de corte
  remision_numero?: string;
  confeccionista_nombre?: string;
  fecha_entrega?: string;
  fecha_entrega_estimada?: string;
  despacha?: boolean;
  estado?: EstadoLote;
  fecha_corte?: string;
  fecha_asignacion?: string;
  observaciones?: string;
  es_pedido_especial?: boolean;
  prioridad?: number;
  cantidad_total_programada?: number;
  detalles?: LoteDetalleCreate[];  // Permitir actualizar detalles
}

// Interfaz básica para OrdenCorte (para trazabilidad)
export interface OrdenCorteBasica {
  id: number;
  numero_orden: string;
  tipo_prenda: string;
  estado: string;
  fecha_creacion: string;
}

