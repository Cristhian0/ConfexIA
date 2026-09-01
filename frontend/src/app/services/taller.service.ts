import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Taller, TallerCreate, TallerUpdate, Remision, RemisionCreate, RemisionUpdate, EstadoRemision } from '../models/taller.model';

@Injectable({
  providedIn: 'root'
})
export class TallerService {
  constructor(private api: ApiService) { }

  // Talleres
  listar(activo?: boolean): Observable<Taller[]> {
    const params = activo !== undefined ? `?activo=${activo}` : '';
    return this.api.get<Taller[]>(`/talleres/${params}`);
  }

  obtener(id: number): Observable<Taller> {
    return this.api.get<Taller>(`/talleres/${id}`);
  }

  crear(taller: TallerCreate): Observable<Taller> {
    return this.api.post<Taller>('/talleres/', taller);
  }

  actualizar(id: number, taller: TallerUpdate): Observable<Taller> {
    return this.api.put<Taller>(`/talleres/${id}`, taller);
  }

  eliminar(id: number): Observable<void> {
    return this.api.delete<void>(`/talleres/${id}`);
  }

  // Remisiones
  listarRemisiones(tallerId?: number, estado?: EstadoRemision): Observable<Remision[]> {
    let params = '';
    if (tallerId) params += `?taller_id=${tallerId}`;
    if (estado) params += params ? `&estado=${estado}` : `?estado=${estado}`;
    return this.api.get<Remision[]>(`/talleres/remisiones${params}`);
  }

  obtenerRemision(id: number): Observable<Remision> {
    return this.api.get<Remision>(`/talleres/remisiones/${id}`);
  }

  crearRemision(remision: RemisionCreate): Observable<Remision> {
    return this.api.post<Remision>('/talleres/remisiones', remision);
  }

  actualizarRemision(id: number, remision: RemisionUpdate): Observable<Remision> {
    return this.api.put<Remision>(`/talleres/remisiones/${id}`, remision);
  }

  actualizarEstadoRemision(id: number, estado: EstadoRemision, revisado_por?: string): Observable<Remision> {
    // El backend espera un objeto (dict) con las claves `estado` y opcionalmente `revisado_por`.
    return this.api.patch<Remision>(`/talleres/remisiones/${id}/estado`, { estado, revisado_por });
  }
}

