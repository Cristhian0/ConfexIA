import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import {
  CostoPrenda,
  RentabilidadLote,
  ProduccionDiaLinea,
  Indicadores
} from '../models/financiero.model';

@Injectable({
  providedIn: 'root'
})
export class FinancieroService {
  constructor(private api: ApiService) { }

  obtenerCostoPrenda(nocId: number): Observable<CostoPrenda> {
    return this.api.get<CostoPrenda>(`/dashboard/costo-prenda?noc_id=${nocId}`);
  }

  obtenerCostoPrendaLote(loteId: number): Observable<CostoPrenda> {
    return this.api.get<CostoPrenda>(`/dashboard/costo-prenda?lote_id=${loteId}`);
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
}
