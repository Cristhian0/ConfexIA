export enum EstadoColilla {
  PENDIENTE = 'pendiente',
  EN_PROCESO = 'en_proceso',
  COMPLETADA = 'completada',
  CANCELADA = 'cancelada'
}

export enum TipoTrabajo {
  ENSAMBLE = 'ensamble',
  COSTURA = 'costura',
  FILETEADO = 'fileteado',
  TERMINACION = 'terminacion',
  OTRO = 'otro'
}

export interface Colilla {
  id: number;
  numero_colilla: string;
  remision_detalle_id?: number;
  lote_id: number;
  taller_id: number;

  // Datos del confeccionista
  confeccionista_nombre: string;
  confeccionista_cedula?: string;

  // Información de trabajo
  tipo_trabajo: TipoTrabajo;
  cantidad_prendas: number;
  descripcion_trabajo?: string;
  referencia?: string;
  talla_id?: number;
  color?: string;

  // Control de cumplimiento
  cantidad_completada: number;
  cantidad_rechazada: number;

  // Estados y fechas
  estado: EstadoColilla;
  fecha_creacion: Date;
  fecha_asignacion?: Date;
  fecha_limite_entrega?: Date;
  fecha_completacion?: Date;

  // Observaciones
  observaciones?: string;
  firma_base64?: string;

  // Metadata
  activa: boolean;
  created_at: Date;
  updated_at?: Date;
}

export interface ColillaListItem {
  id: number;
  numero_colilla: string;
  confeccionista_nombre: string;
  tipo_trabajo: TipoTrabajo;
  cantidad_prendas: number;
  cantidad_completada: number;
  estado: EstadoColilla;
  fecha_creacion: Date;
  fecha_limite_entrega?: Date;
  firma_base64?: string;
}

export interface ColillasPorConfeccionista {
  [confeccionista: string]: {
    confeccionista: string;
    cedula?: string;
    colillas: any[];
    total_colillas: number;
    total_prendas: number;
    total_completadas: number;
    total_rechazadas: number;
  };
}
