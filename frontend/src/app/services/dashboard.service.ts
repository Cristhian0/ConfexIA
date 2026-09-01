import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface Estadisticas {
  lotes_por_estado: { [key: string]: number };
  prendas: {
    total: number;
    en_corte: number;
    en_taller: number;
    confeccionadas: number;
    entregadas: number;
  };
  talleres_activos: number;
  remisiones_pendientes: number;
  fallas_pendientes: number;
  pedidos_especiales: number;
}

export interface RendimientoTaller {
  taller_id: number;
  taller_nombre: string;
  remisiones: number;
  avances: number;
  fallas: number;
  cantidad_confeccionada: number;
  capacidad_diaria: number;
}

export interface AvanceReferencia {
  referencia: string;
  total_programado: number;
  total_completado: number;
  porcentaje_avance: number;
}

export interface AvanceTaller {
  taller: string;
  total_asignado: number;
  total_completado: number;
  porcentaje_avance: number;
}

export interface DetalleColoresTallas {
  referencia: string;
  color: string;
  talla: string;
  programado: number;
  completado: number;
  faltante: number;
}

export interface TiemposProduccion {
  referencia: string;
  tiempo_estimado_dias: number;
  tiempo_real_dias: number;
  diferencia_dias: number;
}

export interface CostoPrenda {
  noc_id?: number;
  lote_id: number;
  total_prendas: number;
  costo_tela: number;
  costo_mano_obra: number;
  costo_insumos: number;
  costo_otros: number;
  costo_total: number;
  costo_unitario: number;
}

export interface RentabilidadLote {
  lote_id: number;
  total_prendas: number;
  anticipo_total: number;
  costo_total: number;
  rentabilidad: number;
  rentabilidad_pct?: number;
  costo_unitario_promedio: number;
}

export interface ProduccionDiaLinea {
  fecha: string;
  linea_produccion?: string;
  cantidad_producida: number;
  cantidad_rechazada: number;
  eficiencia_hph: number;
}

export interface EficienciaOperario {
  operario: string;
  produccion_total: number;
  horas_trabajadas: number;
  piezas_por_hora: number;
}

export interface Indicadores {
  desperdicio_tela_pct: number;
  defectos_pct: number;
  costo_unitario_promedio: number;
  eficiencia_operarios: EficienciaOperario[];
}

export interface ResumenNegocioTextil {
  inventario_tela: { lineas_stock: number; metros_totales: number };
  corte: { ordenes_registradas: number };
  lotes: { activos: number };
  calidad: { inspecciones_registradas: number };
  documentacion: { nocs_generados: number };
}

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  constructor(private api: ApiService) { }

  obtenerEstadisticas(): Observable<Estadisticas> {
    return this.api.get<Estadisticas>('/dashboard/estadisticas');
  }

  obtenerRendimientoTalleres(): Observable<{ talleres: RendimientoTaller[] }> {
    return this.api.get<{ talleres: RendimientoTaller[] }>('/dashboard/rendimiento-talleres');
  }

  obtenerLotesPrioridad(): Observable<{ lotes: any[] }> {
    return this.api.get<{ lotes: any[] }>('/dashboard/lotes-prioridad');
  }

  obtenerAvanceReferencias(): Observable<AvanceReferencia[]> {
    return this.api.get<AvanceReferencia[]>('/dashboard/avance-referencias');
  }

  obtenerAvanceTalleres(): Observable<AvanceTaller[]> {
    return this.api.get<AvanceTaller[]>('/dashboard/avance-talleres');
  }

  obtenerDetalleColoresTallas(): Observable<DetalleColoresTallas[]> {
    return this.api.get<DetalleColoresTallas[]>('/dashboard/detalle-colores-tallas');
  }

  obtenerTiemposProduccion(): Observable<TiemposProduccion[]> {
    return this.api.get<TiemposProduccion[]>('/dashboard/tiempos-produccion');
  }

  obtenerCostoPrenda(nocId: number): Observable<CostoPrenda> {
    return this.api.get<CostoPrenda>(`/dashboard/costo-prenda?noc_id=${nocId}`);
  }

  obtenerRentabilidadLote(loteId: number): Observable<RentabilidadLote> {
    return this.api.get<RentabilidadLote>(`/dashboard/rentabilidad-lote?lote_id=${loteId}`);
  }

  obtenerProduccionDiaLinea(): Observable<ProduccionDiaLinea[]> {
    return this.api.get<ProduccionDiaLinea[]>('/dashboard/produccion-dia-linea');
  }

  obtenerIndicadores(): Observable<Indicadores> {
    return this.api.get<Indicadores>('/dashboard/indicadores');
  }

  obtenerResumenNegocio(): Observable<ResumenNegocioTextil> {
    return this.api.get<ResumenNegocioTextil>('/dashboard/resumen-negocio');
  }
}

