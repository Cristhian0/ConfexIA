import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Router } from '@angular/router';

export interface Accion {
  tipo: string; // 'navegar', 'instrucciones', 'crear', 'registrar'
  titulo: string;
  descripcion: string;
  entidad?: string;
  destino?: string;
  pasos?: string[];
  botones?: any[];
  payload?: any;
}

export interface Mensaje {
  rol: 'usuario' | 'ia';
  contenido: string;
  timestamp?: Date;
  tipo?: string;
  informe?: any;
  acciones?: Accion[];
  sugerencias?: string[];
}

export interface RespuestaChat {
  pregunta: string;
  respuesta: string;
  tipo: string;
  informe_detallado: any;
  acciones?: Accion[];
  sugerencias?: string[];
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private apiUrl = `${environment.apiUrl}/chat`;

  constructor(private http: HttpClient, private router: Router) { }

  enviarPregunta(pregunta: string, contexto?: string): Observable<RespuestaChat> {
    const payload: any = { pregunta };
    if (contexto) {
      payload.contexto = contexto;
    }
    return this.http.post<RespuestaChat>(`${this.apiUrl}/chat`, payload);
  }

  obtenerSugerencias(contexto?: string): Observable<{ sugerencias: string[] }> {
    let url = `${this.apiUrl}/chat/sugerencias`;
    if (contexto) {
      url += `?contexto=${encodeURIComponent(contexto)}`;
    }
    return this.http.get<{ sugerencias: string[] }>(url);
  }

  ejecutarAccion(accion: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/accion`, accion);
  }

  obtenerContextoActual(): string {
    const url = this.router.url;
    const segmentos = url.split('/').filter(s => s);
    
    // Mapear URL a contexto
    const mapa: Record<string, string> = {
      'tela': 'inventario_tela',
      'bodega': 'bodega',
      'corte': 'corte',
      'lotes': 'lotes_produccion',
      'talleres': 'talleres',
      'colillas': 'colillas',
      'calidad': 'calidad',
      'producto-terminado': 'producto_terminado',
      'dashboard': 'dashboard',
      'inicio': 'dashboard',
      'chat-ia': 'chat'
    };

    return mapa[segmentos[0]] || 'general';
  }

  navegarA(destino: string): void {
    if (destino) {
      this.router.navigate([destino]);
    }
  }
}
