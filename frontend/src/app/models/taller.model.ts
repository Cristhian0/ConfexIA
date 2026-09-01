export enum EstadoRemision {
  PENDIENTE = 'pendiente',
  EN_TRANSITO = 'en_transito',
  RECIBIDA = 'recibida',
  PARCIALMENTE_ENTREGADA = 'parcialmente_entregada',
  COMPLETADA = 'completada',
  CANCELADA = 'cancelada'
}

export interface Taller {
  id: number;
  codigo: string;
  nombre: string;
  direccion?: string;
  telefono?: string;
  contacto?: string;
  activo: boolean;
  capacidad_diaria: number;
  created_at: string;
  updated_at?: string;
}

export interface TallerCreate {
  codigo: string;
  nombre: string;
  direccion?: string;
  telefono?: string;
  contacto?: string;
  activo?: boolean;
  capacidad_diaria?: number;
}

export interface TallerUpdate {
  codigo?: string;
  nombre?: string;
  direccion?: string;
  telefono?: string;
  contacto?: string;
  activo?: boolean;
  capacidad_diaria?: number;
}

export interface RemisionDetalleTalla {
  id: number;
  codigo: string;
  nombre: string;
}

export interface RemisionDetalle {
  id: number;
  remision_id: number;
  talla_id: number;
  cantidad: number;
  cantidad_recibida: number;
  cantidad_entregada: number;
  confeccionista_nombre?: string;
  tipo_prenda?: string;
  fecha_entrega_estimada?: string;
  created_at: string;
  updated_at?: string;
  talla?: RemisionDetalleTalla;
}

export interface RemisionDetalleCreate {
  talla_id: number;
  cantidad: number;
  confeccionista_nombre?: string;
  tipo_prenda?: string;
  fecha_entrega_estimada?: string;
}

export interface LoteResumen {
  id: number;
  numero_lote: string;
}

export interface Remision {
  id: number;
  numero_remision: string;
  lote_id: number;
  taller_id: number;
  fecha_remision: string;
  fecha_entrega_estimada?: string;
  fecha_recepcion?: string;
  revisado_por?: string;
  estado: EstadoRemision;
  observaciones?: string;
  created_at: string;
  updated_at?: string;
  detalles: RemisionDetalle[];
  taller?: Taller;
  lote?: LoteResumen;
}

export interface RemisionCreate {
  numero_remision: string;
  lote_id: number;
  taller_id: number;
  fecha_remision: string;
  fecha_entrega_estimada?: string;
  observaciones?: string;
  detalles: RemisionDetalleCreate[];
}

export interface RemisionUpdate {
  numero_remision?: string;
  lote_id?: number;
  taller_id?: number;
  fecha_remision?: string;
  fecha_entrega_estimada?: string;
  fecha_recepcion?: string;
  revisado_por?: string;
  estado?: EstadoRemision;
  observaciones?: string;
}

