import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface OrdenCorteLinea {
  id: number;
  orden_corte_id: number;
  talla_codigo: string;
  cantidad: number;
}

export interface OrdenCorte {
  id: number;
  numero_orden: string;
  tipo_prenda: string;
  estado: string;
  metros_tizado?: number;
  rendimiento_pct?: number;
  piezas_cortadas?: number;
  capas_utilizadas?: number;
  metros_sobrante?: number;
  metros_desperdicio?: number;
  lineas: OrdenCorteLinea[];
  created_at: string;
}

export interface OrdenCorteCreate {
  tipo_prenda: string;
  lineas: { talla_codigo: string; cantidad: number }[];
}

export interface ReservaTela {
  id: number;
  material_id: number;
  color_id: number;
  metros: number;
  orden_corte_id?: number;
  estado: string;
  observaciones?: string;
  material_nombre?: string;
  color_nombre?: string;
  orden_corte_numero?: string;
  created_at: string;
}

export interface ReservaTelaCreate {
  material_id: number;
  color_id: number;
  metros: number;
  orden_corte_id?: number;
  observaciones?: string;
}

export interface OrdenCorteUpdateTizado {
  metros_tizado?: number;
  rendimiento_pct?: number;
}

export interface OrdenCorteUpdateCorte {
  piezas_cortadas?: number;
  capas_utilizadas?: number;
}

export interface OrdenCorteUpdateSobrantes {
  metros_sobrante?: number;
  metros_desperdicio?: number;
}

@Injectable({ providedIn: 'root' })
export class CorteService {
  constructor(private api: ApiService) {}

  listarOrdenes(): Observable<OrdenCorte[]> {
    return this.api.get<OrdenCorte[]>('/corte/ordenes');
  }

  crearOrden(body: OrdenCorteCreate): Observable<OrdenCorte> {
    return this.api.post<OrdenCorte>('/corte/ordenes', body);
  }

  obtenerOrden(ordenId: number): Observable<OrdenCorte> {
    return this.api.get<OrdenCorte>(`/corte/ordenes/${ordenId}`);
  }

  // RF-05: Registrar tizado
  registrarTizado(ordenId: number, data: OrdenCorteUpdateTizado): Observable<OrdenCorte> {
    return this.api.patch<OrdenCorte>(`/corte/ordenes/${ordenId}/tizado`, data);
  }

  // RF-06: Registrar corte
  registrarCorte(ordenId: number, data: OrdenCorteUpdateCorte): Observable<OrdenCorte> {
    return this.api.patch<OrdenCorte>(`/corte/ordenes/${ordenId}/corte`, data);
  }

  // RF-07: Registrar sobrantes
  registrarSobrantes(ordenId: number, data: OrdenCorteUpdateSobrantes): Observable<OrdenCorte> {
    return this.api.patch<OrdenCorte>(`/corte/ordenes/${ordenId}/sobrantes`, data);
  }

  // RF-03: Reservar tela para producción
  listarReservas(): Observable<ReservaTela[]> {
    return this.api.get<ReservaTela[]>('/corte/reservas');
  }

  crearReserva(body: ReservaTelaCreate): Observable<ReservaTela> {
    return this.api.post<ReservaTela>('/corte/reservas', body);
  }

  liberarReserva(reservaId: number): Observable<ReservaTela> {
    return this.api.put<ReservaTela>(`/corte/reservas/${reservaId}/liberar`, {});
  }

  consumirReserva(reservaId: number): Observable<ReservaTela> {
    return this.api.put<ReservaTela>(`/corte/reservas/${reservaId}/consumir`, {});
  }

  listarMovimientosTela(materialId: number, colorId: number): Observable<any[]> {
    return this.api.get<any[]>(`/corte/tela/${materialId}/${colorId}/movimientos`);
  }

  listarMovimientosRollo(rolloId: number): Observable<any[]> {
    return this.api.get<any[]>(`/corte/rollos/${rolloId}/movimientos`);
  }
}
