/**
 * Servicio de Predicciones e IA para Angular
 * Consume endpoints de predicciones del backend
 */

import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface PrediccionDemanda {
  fecha: string;
  cantidad_predicha: number;
  confianza: number;
}

export interface RespuestaPredictorDemanda {
  predicciones: PrediccionDemanda[];
  modelo_entrenado: boolean;
  dias_historicos: number;
  nota?: string;
}

export interface AnomaliaDetectada {
  indice: number;
  severidad: number;
  registro: any;
}

export interface RespuestaDetectorDefectos {
  anomalias_detectadas: number;
  anomalias: AnomaliaDetectada[];
  registros_analizados: number;
  modelo_entrenado: boolean;
}

export interface PuntoReorden {
  punto_reorden: number;
  stock_minimo: number;
  stock_seguridad: number;
  demanda_promedio: number;
  lead_time_dias: number;
  recomendacion: string;
}

export interface CantidadEconomicaOrden {
  cantidad_optima: number;
  costo_anual_total: number;
  numero_ordenes_ano: number;
  dias_entre_ordenes: number;
}

export interface InsightDashboard {
  titulo: string;
  descripcion: string;
  valor_principal: number;
  unidad: string;
  tipo_alerta: 'info' | 'warning' | 'error' | 'success';
  recomendacion?: string;
  datos_adicionales?: any;
}

export interface AnaliseDatos {
  fecha_analisis: string;
  predicciones_demanda?: RespuestaPredictorDemanda;
  anomalias_calidad?: RespuestaDetectorDefectos;
  recomendaciones_inventario?: PuntoReorden;
  insights: InsightDashboard[];
}

@Injectable({
  providedIn: 'root'
})
export class PrediccionesService {
  private apiUrl = `${environment.apiUrl}/predicciones`;

  constructor(private http: HttpClient) {}

  // ============ PREDICCIÓN DE DEMANDA ============

  /**
   * Entrena el modelo de predicción de demanda
   */
  entrenarPredictorDemanda(): Observable<any> {
    return this.http.post(`${this.apiUrl}/entrenar/demanda`, {});
  }

  /**
   * Obtiene predicción de demanda para los próximos N días
   */
  predecirDemanda(dias: number = 7, diasHistoricos: number = 30): Observable<RespuestaPredictorDemanda> {
    let params = new HttpParams()
      .set('dias', dias.toString())
      .set('dias_historicos', diasHistoricos.toString());
    
    return this.http.get<RespuestaPredictorDemanda>(
      `${this.apiUrl}/demanda`,
      { params }
    );
  }

  // ============ DETECCIÓN DE DEFECTOS ============

  /**
   * Entrena el detector de defectos
   */
  entrenarDetectorDefectos(): Observable<any> {
    return this.http.post(`${this.apiUrl}/entrenar/defectos`, {});
  }

  /**
   * Detecta anomalías en registros de defectos
   */
  detectarAnomalias(): Observable<RespuestaDetectorDefectos> {
    return this.http.post<RespuestaDetectorDefectos>(
      `${this.apiUrl}/defectos/detectar`,
      {}
    );
  }

  // ============ INVENTARIO INTELIGENTE ============

  /**
   * Calcula el punto de reorden óptimo
   */
  calcularPuntoReorden(
    demandaPromedio: number,
    leadTimeDias: number = 5,
    desviacionEstandar: number = 10.0,
    factorSeguridad: number = 1.65
  ): Observable<PuntoReorden> {
    let params = new HttpParams()
      .set('demanda_promedio', demandaPromedio.toString())
      .set('lead_time_dias', leadTimeDias.toString())
      .set('desviacion_estandar', desviacionEstandar.toString())
      .set('factor_seguridad', factorSeguridad.toString());
    
    return this.http.post<PuntoReorden>(
      `${this.apiUrl}/inventario/punto-reorden`,
      {},
      { params }
    );
  }

  /**
   * Calcula cantidad económica de orden (EOQ)
   */
  calcularCantidadEconomica(
    demandaAnual: number,
    costoOrden: number = 50.0,
    costoMantenimiento: number = 5.0
  ): Observable<CantidadEconomicaOrden> {
    let params = new HttpParams()
      .set('demanda_anual', demandaAnual.toString())
      .set('costo_orden', costoOrden.toString())
      .set('costo_mantenimiento', costoMantenimiento.toString());
    
    return this.http.post<CantidadEconomicaOrden>(
      `${this.apiUrl}/inventario/cantidad-economica`,
      {},
      { params }
    );
  }

  // ============ DASHBOARD INTELIGENTE ============

  /**
   * Obtiene análisis completo e insights para el dashboard
   */
  obtenerInsights(): Observable<AnaliseDatos> {
    return this.http.get<AnaliseDatos>(
      `${this.apiUrl}/dashboard/insights`
    );
  }

  // ============ FUNCIONES AUXILIARES ============

  /**
   * Mapea tipo de alerta a icono
   */
  getIconoAlerta(tipo: string): string {
    const iconos: Record<string, string> = {
      'info': 'info',
      'warning': 'warning',
      'error': 'error',
      'success': 'check_circle'
    };
    return (iconos as any)[tipo] || 'info';
  }

  /**
   * Mapea tipo de alerta a color
   */
  getColorAlerta(tipo: string): string {
    const colores: Record<string, string> = {
      'info': 'primary',
      'warning': 'warn',
      'error': 'danger',
      'success': 'success'
    };
    return (colores as any)[tipo] || 'primary';
  }
}
