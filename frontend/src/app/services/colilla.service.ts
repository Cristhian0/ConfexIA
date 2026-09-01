import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Colilla, ColillaListItem, ColillasPorConfeccionista, EstadoColilla } from '../models/colilla.model';

@Injectable({
  providedIn: 'root'
})
export class ColillaService {
  private apiUrl = `${environment.apiUrl}/colillas`;

  constructor(private http: HttpClient) { }

  // Listar colillas
  listarColillas(
    skip: number = 0,
    limit: number = 100,
    tallerId?: number,
    loteId?: number,
    confeccionista?: string,
    estado?: EstadoColilla,
    activas: boolean = true
  ): Observable<ColillaListItem[]> {
    let params = new HttpParams();
    params = params.set('skip', skip.toString());
    params = params.set('limit', limit.toString());
    params = params.set('activas', activas.toString());

    if (tallerId) params = params.set('taller_id', tallerId.toString());
    if (loteId) params = params.set('lote_id', loteId.toString());
    if (confeccionista) params = params.set('confeccionista_nombre', confeccionista);
    if (estado) params = params.set('estado', estado);

    return this.http.get<ColillaListItem[]>(`${this.apiUrl}/`, { params });
  }

  // Obtener colillas por confeccionista agrupadas
  colillasPorConfeccionista(
    tallerId: number,
    estado?: EstadoColilla
  ): Observable<ColillasPorConfeccionista> {
    let params = new HttpParams();
    if (estado) params = params.set('estado', estado);

    return this.http.get<ColillasPorConfeccionista>(
      `${this.apiUrl}/por-confeccionista/${tallerId}`,
      { params }
    );
  }

  // Obtener colilla por ID
  obtenerColilla(colillaId: number): Observable<Colilla> {
    return this.http.get<Colilla>(`${this.apiUrl}/${colillaId}`);
  }

  // Crear colilla
  crearColilla(colilla: Partial<Colilla>): Observable<Colilla> {
    return this.http.post<Colilla>(`${this.apiUrl}/`, colilla);
  }

  // Crear múltiples colillas
  crearColillas(loteId: number, colillas: Partial<Colilla>[]): Observable<Colilla[]> {
    return this.http.post<Colilla[]>(`${this.apiUrl}/lote/${loteId}`, colillas);
  }

  // Actualizar colilla
  actualizarColilla(colillaId: number, colilla: Partial<Colilla>): Observable<Colilla> {
    return this.http.put<Colilla>(`${this.apiUrl}/${colillaId}`, colilla);
  }

  // Actualizar estado
  actualizarEstado(
    colillaId: number,
    estado: EstadoColilla,
    cantidadCompletada?: number,
    cantidadRechazada?: number,
    observaciones?: string
  ): Observable<Colilla> {
    return this.http.patch<Colilla>(`${this.apiUrl}/${colillaId}/estado`, {
      estado,
      cantidad_completada: cantidadCompletada,
      cantidad_rechazada: cantidadRechazada,
      observaciones
    });
  }

  // Eliminar colilla
  eliminarColilla(colillaId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${colillaId}`);
  }

  // Obtener estadísticas
  obtenerEstadisticas(tallerId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/stats/taller/${tallerId}`);
  }

  // Descargar PDF de colilla individual
  descargarPdfColilla(colillaId: number): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/pdf/${colillaId}`, { responseType: 'blob' });
  }

  descargarPdfColillaFirmada(colillaId: number, firmaBase64: string): Observable<Blob> {
    return this.http.post(
      `${this.apiUrl}/pdf/${colillaId}/firmar`,
      { firma_base64: firmaBase64 },
      { responseType: 'blob' }
    );
  }

  // Descargar PDF de colillas por taller
  descargarPdfTaller(tallerId: number, estado?: EstadoColilla): Observable<Blob> {
    let params = new HttpParams();
    if (estado) params = params.set('estado', estado);

    return this.http.post(`${this.apiUrl}/pdf/taller/${tallerId}`, {}, { 
      params, 
      responseType: 'blob' 
    });
  }

  // Descargar PDF de colillas por lote
  descargarPdfLote(loteId: number): Observable<Blob> {
    return this.http.post(`${this.apiUrl}/pdf/lote/${loteId}`, {}, { 
      responseType: 'blob' 
    });
  }

  // Abrir y descargar PDF en nueva pestaña
  abrirPdf(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    window.URL.revokeObjectURL(url);
  }

  // Visualizar en navegador
  visualizarPdf(blob: Blob): void {
    const url = window.URL.createObjectURL(blob);
    window.open(url);
  }
}
