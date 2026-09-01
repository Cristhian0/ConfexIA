import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import {
  RolloStock,
  IngresoRolloCreate,
  SalidaRolloCreate,
  RolloMovimiento
} from '../models/inventario-tela.model';

@Injectable({
  providedIn: 'root'
})
export class InventarioTelaService {
  constructor(private api: ApiService) { }

  listarStock(tipo?: string, color?: string, lote?: string): Observable<RolloStock[]> {
    const params: string[] = [];
    if (tipo) params.push(`tipo=${encodeURIComponent(tipo)}`);
    if (color) params.push(`color=${encodeURIComponent(color)}`);
    if (lote) params.push(`lote=${encodeURIComponent(lote)}`);

    const query = params.length ? `?${params.join('&')}` : '';
    return this.api.get<RolloStock[]>(`/inventario-tela/rollos/stock${query}`);
  }

  ingresarRollos(data: IngresoRolloCreate): Observable<RolloMovimiento> {
    return this.api.post<RolloMovimiento>('/inventario-tela/rollos/ingreso', data);
  }

  sacarRollos(data: SalidaRolloCreate): Observable<RolloMovimiento> {
    return this.api.post<RolloMovimiento>('/inventario-tela/rollos/salida', data);
  }

  listarMovimientos(
    material_id?: number,
    color_id?: number,
    orden_corte_id?: number
  ): Observable<RolloMovimiento[]> {
    const params: string[] = [];
    if (material_id) params.push(`material_id=${material_id}`);
    if (color_id) params.push(`color_id=${color_id}`);
    if (orden_corte_id) params.push(`orden_corte_id=${orden_corte_id}`);

    const query = params.length ? `?${params.join('&')}` : '';
    return this.api.get<RolloMovimiento[]>(`/inventario-tela/rollos/movimientos${query}`);
  }
}

