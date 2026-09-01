import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import {
  NOC,
  NOCCreate,
  AlmacenamientoZona,
  AlmacenamientoZonaCreate,
  FinancieroRegistro,
  FinancieroRegistroCreate
} from '../models/documentos.model';

@Injectable({
  providedIn: 'root'
})
export class DocumentosService {
  constructor(private api: ApiService) { }

  // NOC
  listarNoc(remisionId?: number, loteId?: number): Observable<NOC[]> {
    const params: string[] = [];
    if (remisionId) params.push(`remision_id=${remisionId}`);
    if (loteId) params.push(`lote_id=${loteId}`);
    const query = params.length ? `?${params.join('&')}` : '';
    return this.api.get<NOC[]>(`/documentos/noc${query}`);
  }

  crearNoc(noc: NOCCreate): Observable<NOC> {
    return this.api.post<NOC>('/documentos/noc', noc);
  }

  // Almacenamiento
  listarAlmacenamiento(nocId: number): Observable<AlmacenamientoZona[]> {
    return this.api.get<AlmacenamientoZona[]>(`/documentos/noc/${nocId}/almacenamiento`);
  }

  crearAlmacenamiento(data: AlmacenamientoZonaCreate): Observable<AlmacenamientoZona> {
    return this.api.post<AlmacenamientoZona>(`/documentos/noc/${data.noc_id}/almacenamiento`, data);
  }

  // Financiero
  listarFinanciero(nocId: number): Observable<FinancieroRegistro[]> {
    return this.api.get<FinancieroRegistro[]>(`/documentos/noc/${nocId}/financiero`);
  }

  crearFinanciero(data: FinancieroRegistroCreate): Observable<FinancieroRegistro> {
    return this.api.post<FinancieroRegistro>(`/documentos/noc/${data.noc_id}/financiero`, data);
  }
}

