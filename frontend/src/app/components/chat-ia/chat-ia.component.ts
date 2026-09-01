import { Component, OnInit, ViewChild, ElementRef, OnDestroy } from '@angular/core';
import { ChatService, Mensaje, RespuestaChat } from '../../services/chat.service';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-chat-ia',
  templateUrl: './chat-ia.component.html',
  styleUrls: ['./chat-ia.component.scss']
})
export class ChatIaComponent implements OnInit, OnDestroy {
  @ViewChild('chatContainer') chatContainer!: ElementRef;

  mensajes: Mensaje[] = [];
  preguntaActual = '';
  cargando = false;
  sugerencias: string[] = [];
  mostrarSugerencias = true;
  private destroy$ = new Subject<void>();

  constructor(private chatService: ChatService) {
    // Mensaje de bienvenida
    this.mensajes.push({
      rol: 'ia',
      contenido: '¡Hola! Soy tu asistente IA. Puedo ayudarte con análisis de demanda, calidad, inventario y más. ¿Qué necesitas saber?',
      timestamp: new Date()
    });
  }

  ngOnInit(): void {
    const contexto = this.chatService.obtenerContextoActual();
    this.cargarSugerencias(contexto);
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  cargarSugerencias(contexto?: string): void {
    this.chatService.obtenerSugerencias(contexto)
      .pipe(takeUntil(this.destroy$))
      .subscribe(
        data => {
          this.sugerencias = data.sugerencias;
        },
        error => console.error('Error cargando sugerencias:', error)
      );
  }

  enviarPregunta(): void {
    if (!this.preguntaActual.trim()) {
      return;
    }

    // Agregar pregunta del usuario
    this.mensajes.push({
      rol: 'usuario',
      contenido: this.preguntaActual,
      timestamp: new Date()
    });

    const pregunta = this.preguntaActual;
    this.preguntaActual = '';
    this.cargando = true;
    this.mostrarSugerencias = false;

    // Obtener contexto actual
    const contexto = this.chatService.obtenerContextoActual();

    // Enviar al backend con contexto
    this.chatService.enviarPregunta(pregunta, contexto)
      .pipe(takeUntil(this.destroy$))
      .subscribe(
        (respuesta: RespuestaChat) => {
          this.mensajes.push({
            rol: 'ia',
            contenido: respuesta.respuesta,
            timestamp: new Date(),
            tipo: respuesta.tipo,
            informe: respuesta.informe_detallado,
            acciones: respuesta.acciones,
            sugerencias: respuesta.sugerencias
          });
          this.cargando = false;
          this.scrollAlFinal();
        },
        error => {
          console.error('Error:', error);
          this.mensajes.push({
            rol: 'ia',
            contenido: 'Lo siento, hubo un error procesando tu pregunta. Intenta de nuevo.',
            timestamp: new Date()
          });
          this.cargando = false;
        }
      );

    this.scrollAlFinal();
  }

  usarSugerencia(sugerencia: string): void {
    this.preguntaActual = sugerencia;
    setTimeout(() => {
      this.enviarPregunta();
    }, 100);
  }

  scrollAlFinal(): void {
    setTimeout(() => {
      if (this.chatContainer) {
        this.chatContainer.nativeElement.scrollTop = this.chatContainer.nativeElement.scrollHeight;
      }
    }, 100);
  }

  getColorTipo(tipo: string): string {
    const colores: Record<string, string> = {
      'demanda': '#FF9800',
      'calidad': '#F44336',
      'inventario': '#4CAF50',
      'general': '#2196F3'
    };
    return colores[tipo] || '#757575';
  }

  getIconoTipo(tipo: string): string {
    const iconos: Record<string, string> = {
      'demanda': 'trending_up',
      'calidad': 'verified_user',
      'inventario': 'store',
      'general': 'info'
    };
    return iconos[tipo] || 'info';
  }

  abrirDetalles(mensaje: Mensaje): void {
    if (mensaje.informe) {
      console.log('Informe detallado:', mensaje.informe);
      // Aquí podrías abrir un modal con el informe completo
    }
  }

  limpiarChat(): void {
    this.mensajes = [{
      rol: 'ia',
      contenido: '¡Hola! Soy tu asistente IA. Puedo ayudarte con análisis de demanda, calidad, inventario y más. ¿Qué necesitas saber?',
      timestamp: new Date()
    }];
    this.mostrarSugerencias = true;
    this.scrollAlFinal();
  }

  ejecutarAccion(accion: any): void {
    if (accion.tipo === 'navegar' && accion.destino) {
      this.chatService.navegarA(accion.destino);
      return;
    }

    if (!accion.payload || !accion.entidad) {
      this.mensajes.push({
        rol: 'ia',
        contenido: 'Esta acción es una sugerencia. Envío la pregunta o completa la información para que pueda ejecutarla.',
        timestamp: new Date(),
        tipo: 'accion'
      });
      return;
    }

    this.cargando = true;
    this.chatService.ejecutarAccion(accion)
      .pipe(takeUntil(this.destroy$))
      .subscribe(
        response => {
          const contenido = response.exitoso
            ? `✅ Acción ejecutada: ${response.mensaje}`
            : `⚠️ No se ejecutó la acción: ${response.mensaje}`;
          const detalles = response.faltan_campos ? `
Faltan campos: ${response.faltan_campos.join(', ')}` : '';

          this.mensajes.push({
            rol: 'ia',
            contenido: contenido + detalles,
            timestamp: new Date(),
            tipo: response.exitoso ? 'accion' : 'error',
            informe: response.payload || response.resultado || null
          });
          this.cargando = false;
          this.scrollAlFinal();
        },
        error => {
          console.error('Error ejecutando acción:', error);
          const message = error?.error?.detail || error?.message || 'Lo siento, no pude ejecutar la acción. Revisa los datos e intenta nuevamente.';
          this.mensajes.push({
            rol: 'ia',
            contenido: `⚠️ No se pudo ejecutar la acción. ${message}`,
            timestamp: new Date(),
            tipo: 'error'
          });
          this.cargando = false;
        }
      );
  }

  navegarA(destino: string): void {
    this.chatService.navegarA(destino);
  }
}
