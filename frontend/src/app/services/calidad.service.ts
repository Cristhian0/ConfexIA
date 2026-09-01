import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  InspeccionCalidad,
  InspeccionCalidadCreate,
  InspeccionCalidadUpdate,
  DefectoInspeccionCreate,
  DefectoInspeccion
} from '../models/produccion.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class CalidadService {
  private apiUrl = `${environment.apiUrl}/calidad`;

  constructor(private http: HttpClient) {}

  // RF-15: Crear inspección de calidad
  crearInspeccion(datos: InspeccionCalidadCreate): Observable<InspeccionCalidad> {
    return this.http.post<InspeccionCalidad>(`${this.apiUrl}/inspecciones`, datos);
  }

  // RF-15: Listar inspecciones con filtros
  listarInspecciones(
    ordenId?: number,
    clasificacion?: string,
    inspector?: string
  ): Observable<InspeccionCalidad[]> {
    let params = new HttpParams();
    if (ordenId) params = params.set('orden_id', ordenId.toString());
    if (clasificacion) params = params.set('clasificacion', clasificacion);
    if (inspector) params = params.set('inspector', inspector);

    return this.http.get<InspeccionCalidad[]>(`${this.apiUrl}/inspecciones`, { params });
  }

  // RF-15: Obtener inspección individual
  obtenerInspeccion(id: number): Observable<InspeccionCalidad> {
    return this.http.get<InspeccionCalidad>(`${this.apiUrl}/inspecciones/${id}`);
  }

  // RF-16: Actualizar clasificación e inspección
  actualizarInspeccion(
    id: number,
    datos: InspeccionCalidadUpdate
  ): Observable<InspeccionCalidad> {
    return this.http.patch<InspeccionCalidad>(
      `${this.apiUrl}/inspecciones/${id}`,
      datos
    );
  }

  // Obtener resumen con porcentajes
  obtenerResumenInspeccion(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/inspecciones/${id}/resumen`);
  }

  // RF-17: Agregar defecto a inspección
  agregarDefecto(
    inspeccionId: number,
    defecto: DefectoInspeccionCreate
  ): Observable<DefectoInspeccion> {
    return this.http.post<DefectoInspeccion>(
      `${this.apiUrl}/inspecciones/${inspeccionId}/defectos`,
      defecto
    );
  }

  // RF-17: Listar defectos de una inspección
  listarDefectos(inspeccionId: number): Observable<DefectoInspeccion[]> {
    return this.http.get<DefectoInspeccion[]>(
      `${this.apiUrl}/inspecciones/${inspeccionId}/defectos`
    );
  }

  // RF-17: Eliminar defecto
  eliminarDefecto(defectoId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/defectos/${defectoId}`);
  }

  // RF-18: Marcar prenda para reingresar a producción
  marcarReingresar(inspeccionId: number): Observable<InspeccionCalidad> {
    return this.http.post<InspeccionCalidad>(
      `${this.apiUrl}/inspecciones/${inspeccionId}/reingresar`,
      {}
    );
  }

  // RF-18: Verificar si puede reingresar a producción
  verificarPuedeReingresar(inspeccionId: number): Observable<{ puede_reingresar: boolean }> {
    return this.http.get<{ puede_reingresar: boolean }>(
      `${this.apiUrl}/inspecciones/${inspeccionId}/puede-reingresar`
    );
  }
}
