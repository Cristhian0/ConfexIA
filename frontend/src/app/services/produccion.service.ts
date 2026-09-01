import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import {
  OrdenProduccion,
  OrdenProduccionCreate,
  OrdenProduccionUpdate,
  RegistroProduccion,
  RegistroProduccionCreate,
  RegistroProduccionUpdate,
  EstadoOrdenProduccion
} from '../models/produccion.model';

@Injectable({ providedIn: 'root' })
export class ProduccionService {
  constructor(private api: ApiService) {}

  // ========== ÓRDENES DE PRODUCCIÓN ==========

  /**
   * RF-11: Listar órdenes de producción
   */
  listarOrdenes(
    loteId?: number,
    estado?: EstadoOrdenProduccion,
    skip?: number,
    limit?: number
  ): Observable<OrdenProduccion[]> {
    let params: string[] = [];
    if (skip !== undefined) params.push(`skip=${skip}`);
    if (limit !== undefined) params.push(`limit=${limit}`);
    if (loteId !== undefined) params.push(`lote_id=${loteId}`);
    if (estado !== undefined) params.push(`estado=${estado}`);

    const queryString = params.length > 0 ? `?${params.join('&')}` : '';
    return this.api.get<OrdenProduccion[]>(`/produccion/ordenes${queryString}`);
  }

  /**
   * RF-11: Crear nueva orden de confección
   */
  crearOrden(datos: OrdenProduccionCreate): Observable<OrdenProduccion> {
    return this.api.post<OrdenProduccion>('/produccion/ordenes', datos);
  }

  /**
   * Obtener una orden de producción específica
   */
  obtenerOrden(ordenId: number): Observable<OrdenProduccion> {
    return this.api.get<OrdenProduccion>(`/produccion/ordenes/${ordenId}`);
  }

  /**
   * Actualizar estado o información de una orden
   */
  actualizarOrden(ordenId: number, datos: OrdenProduccionUpdate): Observable<OrdenProduccion> {
    return this.api.patch<OrdenProduccion>(`/produccion/ordenes/${ordenId}`, datos);
  }

  /**
   * Marcar una orden como completada
   */
  completarOrden(ordenId: number): Observable<OrdenProduccion> {
    return this.api.post<OrdenProduccion>(`/produccion/ordenes/${ordenId}/completar`, {});
  }

  // ========== REGISTROS DE PRODUCCIÓN ==========

  /**
   * RF-12, RF-13, RF-14: Listar registros de producción
   * Filtros disponibles: orden_produccion_id, operario, linea_produccion
   */
  listarRegistros(
    ordenId?: number,
    operario?: string,
    lineaProduccion?: string,
    skip?: number,
    limit?: number
  ): Observable<RegistroProduccion[]> {
    let params: string[] = [];
    if (skip !== undefined) params.push(`skip=${skip}`);
    if (limit !== undefined) params.push(`limit=${limit}`);
    if (ordenId !== undefined) params.push(`orden_produccion_id=${ordenId}`);
    if (operario !== undefined) params.push(`operario=${encodeURIComponent(operario)}`);
    if (lineaProduccion !== undefined) params.push(`linea_produccion=${lineaProduccion}`);

    const queryString = params.length > 0 ? `?${params.join('&')}` : '';
    return this.api.get<RegistroProduccion[]>(`/produccion/registros${queryString}`);
  }

  /**
   * RF-12: Registrar producción por operación
   * RF-13: Control por operario o línea
   * RF-14: Registrar tiempos de producción
   */
  crearRegistro(datos: RegistroProduccionCreate): Observable<RegistroProduccion> {
    return this.api.post<RegistroProduccion>('/produccion/registros', datos);
  }

  /**
   * Obtener un registro de producción específico
   */
  obtenerRegistro(registroId: number): Observable<RegistroProduccion> {
    return this.api.get<RegistroProduccion>(`/produccion/registros/${registroId}`);
  }

  /**
   * Actualizar un registro de producción (por ejemplo, completar tiempo_fin)
   */
  actualizarRegistro(registroId: number, datos: RegistroProduccionUpdate): Observable<RegistroProduccion> {
    return this.api.patch<RegistroProduccion>(`/produccion/registros/${registroId}`, datos);
  }

  /**
   * Eliminar un registro de producción
   */
  eliminarRegistro(registroId: number): Observable<void> {
    return this.api.delete<void>(`/produccion/registros/${registroId}`);
  }

  /**
   * Obtener registros por orden de producción (agrupados)
   */
  obtenerRegistrosPorOrden(ordenId: number): Observable<RegistroProduccion[]> {
    return this.listarRegistros(ordenId);
  }

  /**
   * Obtener resumen de producción de una orden
   */
  obtenerResumenOrden(ordenId: number): Observable<any> {
    return this.api.get<any>(`/produccion/ordenes/${ordenId}/resumen`);
  }
}

