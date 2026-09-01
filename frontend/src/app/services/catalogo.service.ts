import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Talla, TallaCreate, TallaUpdate } from '../models/talla.model';
import { Color, ColorCreate, ColorUpdate } from '../models/color.model';
import { Material, MaterialCreate, MaterialUpdate } from '../models/material.model';
import { Referencia, ReferenciaCreate, ReferenciaUpdate } from '../models/referencia.model';

@Injectable({
  providedIn: 'root'
})
export class CatalogoService {
  constructor(private api: ApiService) { }

  // Tallas
  listarTallas(activo?: boolean): Observable<Talla[]> {
    const params = activo !== undefined ? `?activo=${activo}` : '';
    return this.api.get<Talla[]>(`/catalogo/tallas${params}`);
  }

  crearTalla(talla: TallaCreate): Observable<Talla> {
    return this.api.post<Talla>('/catalogo/tallas', talla);
  }

  actualizarTalla(id: number, talla: TallaUpdate): Observable<Talla> {
    return this.api.put<Talla>(`/catalogo/tallas/${id}`, talla);
  }

  eliminarTalla(id: number): Observable<void> {
    return this.api.delete<void>(`/catalogo/tallas/${id}`);
  }

  // Colores
  listarColores(activo?: boolean): Observable<Color[]> {
    const params = activo !== undefined ? `?activo=${activo}` : '';
    return this.api.get<Color[]>(`/catalogo/colores${params}`);
  }

  crearColor(color: ColorCreate): Observable<Color> {
    return this.api.post<Color>('/catalogo/colores', color);
  }

  actualizarColor(id: number, color: ColorUpdate): Observable<Color> {
    return this.api.put<Color>(`/catalogo/colores/${id}`, color);
  }

  eliminarColor(id: number): Observable<void> {
    return this.api.delete<void>(`/catalogo/colores/${id}`);
  }

  // Materiales
  listarMateriales(activo?: boolean): Observable<Material[]> {
    const params = activo !== undefined ? `?activo=${activo}` : '';
    return this.api.get<Material[]>(`/catalogo/materiales${params}`);
  }

  crearMaterial(material: MaterialCreate): Observable<Material> {
    return this.api.post<Material>('/catalogo/materiales', material);
  }

  actualizarMaterial(id: number, material: MaterialUpdate): Observable<Material> {
    return this.api.put<Material>(`/catalogo/materiales/${id}`, material);
  }

  eliminarMaterial(id: number): Observable<void> {
    return this.api.delete<void>(`/catalogo/materiales/${id}`);
  }

  // Referencias
  listarReferencias(activo?: boolean): Observable<Referencia[]> {
    const params = activo !== undefined ? `?activo=${activo}` : '';
    return this.api.get<Referencia[]>(`/catalogo/referencias${params}`);
  }

  crearReferencia(referencia: ReferenciaCreate): Observable<Referencia> {
    return this.api.post<Referencia>('/catalogo/referencias', referencia);
  }

  actualizarReferencia(id: number, referencia: ReferenciaUpdate): Observable<Referencia> {
    return this.api.put<Referencia>(`/catalogo/referencias/${id}`, referencia);
  }

  eliminarReferencia(id: number): Observable<void> {
    return this.api.delete<void>(`/catalogo/referencias/${id}`);
  }
}

