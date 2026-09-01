import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import {
  ProductoTerminadoStock,
  ProductoTerminadoStockCreate,
  ProductoTerminadoStockUpdate,
  ProductoTerminadoMovimiento,
  ZonaAlmacen
} from '../models/producto-terminado.model';

@Injectable({
  providedIn: 'root'
})
export class ProductoTerminadoService {
  constructor(private api: ApiService) { }

  listarStock(
    sku?: string,
    tipo?: string,
    tallaId?: number,
    colorId?: number,
    zona?: ZonaAlmacen
  ): Observable<ProductoTerminadoStock[]> {
    const params: string[] = [];
    if (sku) params.push(`sku=${encodeURIComponent(sku)}`);
    if (tipo) params.push(`tipo=${encodeURIComponent(tipo)}`);
    if (tallaId !== undefined) params.push(`talla_id=${tallaId}`);
    if (colorId !== undefined) params.push(`color_id=${colorId}`);
    if (zona) params.push(`zona=${zona}`);

    const query = params.length ? `?${params.join('&')}` : '';
    return this.api.get<ProductoTerminadoStock[]>(`/inventario-pt/stock${query}`);
  }

  obtenerStock(id: number): Observable<ProductoTerminadoStock> {
    return this.api.get<ProductoTerminadoStock>(`/inventario-pt/stock/${id}`);
  }

  ingresarStock(data: ProductoTerminadoStockCreate): Observable<ProductoTerminadoStock> {
    return this.api.post<ProductoTerminadoStock>(`/inventario-pt/stock/ingreso`, data);
  }

  actualizarStock(id: number, data: ProductoTerminadoStockUpdate): Observable<ProductoTerminadoStock> {
    return this.api.patch<ProductoTerminadoStock>(`/inventario-pt/stock/${id}`, data);
  }

  listarMovimientos(stockId: number): Observable<ProductoTerminadoMovimiento[]> {
    return this.api.get<ProductoTerminadoMovimiento[]>(`/inventario-pt/stock/${stockId}/movimientos`);
  }
}
