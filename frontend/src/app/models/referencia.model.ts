export interface Referencia {
  id: number;
  codigo: string;
  nombre: string;
  descripcion?: string;
  es_pedido_especial: boolean;
  activo: boolean;
  created_at: string;
  updated_at?: string;
}

export interface ReferenciaCreate {
  codigo: string;
  nombre: string;
  descripcion?: string;
  es_pedido_especial?: boolean;
  activo?: boolean;
}

export interface ReferenciaUpdate {
  codigo?: string;
  nombre?: string;
  descripcion?: string;
  es_pedido_especial?: boolean;
  activo?: boolean;
}

