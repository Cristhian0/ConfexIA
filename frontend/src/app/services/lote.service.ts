import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Lote, LoteCreate, LoteUpdate, EstadoLote } from '../models/lote.model';

@Injectable({
  providedIn: 'root'
})
export class LoteService {
  constructor(private api: ApiService) { }

  listar(estado?: EstadoLote, esPedidoEspecial?: boolean): Observable<Lote[]> {
    let params = '';
    if (estado) params += `?estado=${estado}`;
    if (esPedidoEspecial !== undefined) {
      params += params ? `&es_pedido_especial=${esPedidoEspecial}` : `?es_pedido_especial=${esPedidoEspecial}`;
    }
    return this.api.get<Lote[]>(`/lotes-produccion${params}`);
  }

  obtener(id: number): Observable<Lote> {
    return this.api.get<Lote>(`/lotes-produccion/${id}`);
  }

  crear(lote: LoteCreate): Observable<Lote> {
    return this.api.post<Lote>('/lotes-produccion/', lote);
  }

  actualizar(id: number, lote: LoteUpdate): Observable<Lote> {
    return this.api.put<Lote>(`/lotes-produccion/${id}`, lote);
  }

  eliminar(id: number): Observable<void> {
    return this.api.delete<void>(`/lotes-produccion/${id}`);
  }

  actualizarEstado(id: number, estado: EstadoLote): Observable<Lote> {
    return this.api.patch<Lote>(`/lotes-produccion/${id}/estado`, { estado: estado });
  }
}

