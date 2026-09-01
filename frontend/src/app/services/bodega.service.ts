import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import {
  ProductoTerminadoStock,
  ProductoTerminadoSalidaCreate
} from '../models/producto-terminado.model';

@Injectable({
  providedIn: 'root'
})
export class BodegaService {
  constructor(private api: ApiService) { }

  listarStock(
    sku?: string,
    tipo?: string,
    tallaId?: number,
    colorId?: number,
    zona?: string
  ): Observable<ProductoTerminadoStock[]> {
    const params: string[] = [];
    if (sku) params.push(`sku=${encodeURIComponent(sku)}`);
    if (tipo) params.push(`tipo=${encodeURIComponent(tipo)}`);
    if (tallaId !== undefined) params.push(`talla_id=${tallaId}`);
    if (colorId !== undefined) params.push(`color_id=${colorId}`);
    if (zona) params.push(`zona=${zona}`);
    const query = params.length ? `?${params.join('&')}` : '';
    return this.api.get<ProductoTerminadoStock[]>(`/bodega/stock${query}`);
  }

  obtenerStock(id: number) {
    return this.api.get<ProductoTerminadoStock>(`/bodega/stock/${id}`);
  }

  registrarSalida(id: number, data: ProductoTerminadoSalidaCreate) {
    return this.api.post<ProductoTerminadoStock>(`/bodega/stock/${id}/salida`, data);
  }
}

