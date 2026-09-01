export enum TipoFalla {
  DEFECTO_TELA = 'defecto_tela',
  DEFECTO_CONFECCION = 'defecto_confeccion',
  DEFECTO_COLOR = 'defecto_color',
  DEFECTO_TALLA = 'defecto_talla',
  OTRO = 'otro'
}

export enum EstadoFalla {
  REPORTADA = 'reportada',
  EN_REVISION = 'en_revision',
  CORREGIDA = 'corregida',
  RECHAZADA = 'rechazada'
}

// ========== RF-11, RF-12, RF-13, RF-14: Órdenes de Producción ==========
export enum EstadoOrdenProduccion {
  PENDIENTE = 'pendiente',
  EN_PROGRESO = 'en_progreso',
  COMPLETADA = 'completada',
  CANCELADA = 'cancelada'
}

export enum TipoOperacion {
  ENSAMBLE = 'ensamble',
  COSTURA = 'costura',
  FILETEADO = 'fileteado',
  TERMINACION = 'terminacion'
}

export interface RegistroProduccion {
  id: number;
  orden_produccion_id: number;
  operacion: TipoOperacion;
  operario: string;
  linea_produccion?: string;
  cantidad_producida: number;
  cantidad_rechazada: number;
  tiempo_inicio: string;
  tiempo_fin?: string;
  tiempo_total_minutos?: number;
  notas?: string;
  created_at: string;
  updated_at?: string;
}

export interface RegistroProduccionCreate {
  orden_produccion_id: number;
  operacion: TipoOperacion;
  operario: string;
  linea_produccion?: string;
  cantidad_producida: number;
  cantidad_rechazada: number;
  tiempo_inicio: string;
  tiempo_fin?: string;
  notas?: string;
}

export interface RegistroProduccionUpdate {
  operario?: string;
  linea_produccion?: string;
  cantidad_producida?: number;
  cantidad_rechazada?: number;
  tiempo_fin?: string;
  notas?: string;
}

export interface OrdenProduccion {
  id: number;
  numero_orden: string;
  lote_id: number;
  estado: EstadoOrdenProduccion;
  fecha_creacion: string;
  fecha_inicio?: string;
  fecha_fin?: string;
  observaciones?: string;
  fecha_recepcion?: string;
  revisado_por?: string;
  cantidad_parcial?: number;
  cantidad_arreglos?: number;
  cantidad_imperfecciones?: number;
  cantidad_pendiente?: number;
  requiere_compras?: boolean;
  fecha_entrega_total?: string;
  dias_mora?: number;
  estado_pago?: string;
  created_at: string;
  updated_at?: string;
  registros_produccion?: RegistroProduccion[];
}

export interface OrdenProduccionCreate {
  lote_id: number;
  observaciones?: string;
}

export interface OrdenProduccionUpdate {
  estado?: EstadoOrdenProduccion;
  fecha_inicio?: string;
  fecha_fin?: string;
  observaciones?: string;
}

export interface AvanceProduccion {
  id: number;
  lote_id: number;
  taller_id: number;
  remision_id?: number;
  fecha_avance: string;
  cantidad_avance: number;
  porcentaje_avance: number;
  observaciones?: string;
  created_at: string;
}

export interface AvanceProduccionCreate {
  lote_id: number;
  taller_id: number;
  remision_id?: number;
  fecha_avance: string;
  cantidad_avance: number;
  porcentaje_avance: number;
  observaciones?: string;
}

export interface FallaConfeccion {
  id: number;
  lote_id: number;
  remision_id?: number;
  taller_id?: number;
  tipo_falla: TipoFalla;
  estado: EstadoFalla;
  cantidad_afectada: number;
  descripcion: string;
  accion_correctiva?: string;
  fecha_reporte: string;
  fecha_resolucion?: string;
  created_at: string;
  updated_at?: string;
}

export interface FallaConfeccionCreate {
  lote_id: number;
  remision_id?: number;
  taller_id?: number;
  tipo_falla: TipoFalla;
  cantidad_afectada: number;
  descripcion: string;
  fecha_reporte: string;
}

export interface FallaConfeccionUpdate {
  lote_id?: number;
  remision_id?: number;
  taller_id?: number;
  tipo_falla?: TipoFalla;
  estado?: EstadoFalla;
  cantidad_afectada?: number;
  descripcion?: string;
  accion_correctiva?: string;
  fecha_reporte?: string;
  fecha_resolucion?: string;
}

export enum EstadoControlCalidad {
  PENDIENTE_INSPECCION = 'pendiente_inspeccion',
  EN_INSPECCION = 'en_inspeccion',
  APROBADO = 'aprobado',
  CON_IMPERFECCIONES = 'con_imperfecciones',
  DEVUELTO_TALLER = 'devuelto_taller',
  EN_REPARACION = 'en_reparacion',
  REPARADO = 'reparado',
  RECHAZADO = 'rechazado'
}

export enum TipoImperfecto {
  DEFECTO_TELA = 'defecto_tela',
  DEFECTO_CONFECCION = 'defecto_confeccion',
  DEFECTO_COLOR = 'defecto_color',
  DEFECTO_TALLA = 'defecto_talla',
  MEDIDAS_INCORRECTAS = 'medidas_incorrectas',
  ACABADO_DEFICIENTE = 'acabado_deficiente',
  OTRO = 'otro'
}

export interface ImperfectoCalidad {
  id: number;
  control_calidad_id: number;
  tipo_imperfecto: TipoImperfecto;
  cantidad_afectada: number;
  descripcion: string;
  causa?: string;
  arreglo_requerido?: string;
  estado_arreglo: EstadoControlCalidad;
  fecha_reporte: string;
  fecha_arreglo?: string;
}

export interface ImperfectoCalidadCreate {
  tipo_imperfecto: TipoImperfecto;
  cantidad_afectada: number;
  descripcion: string;
  causa?: string;
  arreglo_requerido?: string;
}

export interface ImperfectoCalidadUpdate {
  tipo_imperfecto?: TipoImperfecto;
  cantidad_afectada?: number;
  descripcion?: string;
  causa?: string;
  arreglo_requerido?: string;
  estado_arreglo?: EstadoControlCalidad;
  fecha_arreglo?: string;
}

export interface ControlCalidad {
  id: number;
  lote_id: number;
  remision_id: number;
  fecha_inspeccion: string;
  inspector: string;
  estado: EstadoControlCalidad;
  cantidad_recibida: number;
  cantidad_aprobada: number;
  cantidad_imperfecciones: number;
  cantidad_pendiente_confeccion: number;
  cantidad_devuelta: number;
  // Nuevos campos
  fecha_recepcion?: string;
  revisado_por?: string;
  cantidad_parcial?: number;
  cantidad_arreglos?: number;
  tiene_imperfecciones?: boolean;
  cantidad_pendiente?: number;
  requiere_compras?: boolean;
  fecha_entrega_total?: string;
  dias_mora?: number;
  estado_pago?: string;
  observaciones_generales?: string;
  fecha_devolucion?: string;
  fecha_recepcion_reparado?: string;
  created_at: string;
  updated_at?: string;
  lote?: any; // LoteResumen
  remision?: any; // RemisionResumen
  imperfectos: ImperfectoCalidad[];
}

export interface ControlCalidadCreate {
  lote_id: number;
  remision_id: number;
  fecha_inspeccion: string;
  inspector: string;
  cantidad_recibida: number;
  // Nuevos campos opcionales en creación
  fecha_recepcion?: string;
  revisado_por?: string;
  cantidad_parcial?: number;
  cantidad_arreglos?: number;
  tiene_imperfecciones?: boolean;
  cantidad_pendiente?: number;
  requiere_compras?: boolean;
  fecha_entrega_total?: string;
  dias_mora?: number;
  estado_pago?: string;
  cantidad_aprobada?: number;
  cantidad_imperfecciones?: number;
  cantidad_pendiente_confeccion?: number;
  cantidad_devuelta?: number;
  observaciones_generales?: string;
  imperfectos?: ImperfectoCalidadCreate[];
}

export interface ControlCalidadUpdate {
  lote_id?: number;
  remision_id?: number;
  fecha_inspeccion?: string;
  inspector?: string;
  estado?: EstadoControlCalidad;
  cantidad_recibida?: number;
  // Nuevos campos editables
  fecha_recepcion?: string;
  revisado_por?: string;
  cantidad_parcial?: number;
  cantidad_arreglos?: number;
  tiene_imperfecciones?: boolean;
  cantidad_pendiente?: number;
  requiere_compras?: boolean;
  fecha_entrega_total?: string;
  dias_mora?: number;
  estado_pago?: string;
  cantidad_aprobada?: number;
  cantidad_imperfecciones?: number;
  cantidad_pendiente_confeccion?: number;
  cantidad_devuelta?: number;
  observaciones_generales?: string;
  fecha_devolucion?: string;
  fecha_recepcion_reparado?: string;
}

// ========== RF-15 a RF-18: Control de Calidad ==========

export enum TipoDefecto {
  COSTURA = 'costura',
  MEDIDA = 'medida',
  MANCHA = 'mancha',
  TELA = 'tela'
}

export enum ClasificacionInspeccion {
  OK = 'ok',
  REPROCESO = 'reproceso',
  DEFECTUOSA = 'defectuosa'
}

export interface DefectoInspeccion {
  id: number;
  tipo_defecto: TipoDefecto;
  cantidad_defectos: number;
  descripcion?: string;
  recomendacion?: string;
  created_at: string;
}

export interface DefectoInspeccionCreate {
  tipo_defecto: TipoDefecto;
  cantidad_defectos: number;
  descripcion?: string;
  recomendacion?: string;
}

export interface InspeccionCalidad {
  id: number;
  numero_inspeccion: string;
  orden_produccion_id: number;
  inspector: string;
  clasificacion: ClasificacionInspeccion;
  cantidad_inspeccionada: number;
  cantidad_ok: number;
  cantidad_reproceso: number;
  cantidad_defectuosa: number;
  observaciones?: string;
  reingresar_produccion: boolean; // RF-18
  fecha_inspeccion: string;
  created_at: string;
  updated_at?: string;
  defectos?: DefectoInspeccion[];
}

export interface InspeccionCalidadCreate {
  orden_produccion_id: number;
  inspector: string;
  clasificacion: ClasificacionInspeccion;
  cantidad_inspeccionada: number;
  cantidad_ok: number;
  cantidad_reproceso: number;
  cantidad_defectuosa: number;
  observaciones?: string;
  reingresar_produccion: boolean;
}

export interface InspeccionCalidadUpdate {
  clasificacion?: ClasificacionInspeccion;
  cantidad_ok?: number;
  cantidad_reproceso?: number;
  cantidad_defectuosa?: number;
  observaciones?: string;
  reingresar_produccion?: boolean;
}

