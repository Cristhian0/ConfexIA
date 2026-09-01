import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { ChatService } from '../../services/chat.service';

@Component({
  selector: 'app-chat-floating-button',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatIconModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatTooltipModule
  ],
  template: `
    <!-- Botón flotante -->
    <div class="chat-floating-container">
      <!-- Avatar/Botón flotante -->
      <button 
        class="chat-float-button" 
        (click)="abrirChat()"
        [class.active]="chatAbierto"
        matTooltip="Asistente IA">
        <mat-icon class="icon-robot">smart_toy</mat-icon>
        <span class="badge" *ngIf="!chatAbierto">💬</span>
      </button>

      <!-- Panel flotante del chat -->
      <div class="chat-panel" *ngIf="chatAbierto">
        <div class="chat-panel-header">
          <h3>Asistente IA</h3>
          <button mat-icon-button (click)="cerrarChat()" class="close-btn">
            <mat-icon>close</mat-icon>
          </button>
        </div>

        <!-- Mini chat -->
        <div class="chat-panel-messages">
          <div *ngFor="let msg of mensajesCompacto" 
               class="mensaje" 
               [class.usuario]="msg.rol === 'usuario'"
               [class.ia]="msg.rol === 'ia'">
            <div class="mensaje-bubble">
              {{ msg.contenido | slice:0:100 }}{{ msg.contenido.length > 100 ? '...' : '' }}
            </div>
            <!-- Acciones si las hay -->
            <div *ngIf="msg.acciones && msg.acciones.length > 0" class="acciones-flotantes">
              <button 
                *ngFor="let accion of msg.acciones" 
                mat-stroked-button 
                class="btn-accion-flotante"
                (click)="ejecutarAccion(accion)">
                <mat-icon>rocket_launch</mat-icon>
                {{ accion.titulo | slice:0:20 }}
              </button>
            </div>
          </div>
        </div>

        <!-- Sugerencias rápidas -->
        <div class="chat-panel-suggestions" *ngIf="sugerencias.length > 0">
          <div class="suggestion-row">
            <span>Preguntas rápidas</span>
          </div>
          <div class="suggestion-chips">
            <button mat-stroked-button *ngFor="let sugerencia of sugerencias | slice:0:4" class="suggestion-chip" (click)="usarSugerencia(sugerencia)">
              {{ sugerencia }}
            </button>
          </div>
        </div>

        <!-- Sugerencias rápidas -->
        <div class="chat-panel-suggestions" *ngIf="sugerencias.length > 0">
          <div class="suggestion-row">
            <span>Preguntas sugeridas</span>
          </div>
          <div class="suggestion-chips">
            <button mat-stroked-button *ngFor="let sugerencia of sugerencias | slice:0:4" class="suggestion-chip" (click)="usarSugerencia(sugerencia)">
              {{ sugerencia }}
            </button>
          </div>
        </div>

        <!-- Input compacto -->
        <div class="chat-panel-input">
          <mat-form-field appearance="outline" class="compact-input">
            <input 
              matInput 
              [(ngModel)]="preguntaRapida" 
              (keyup.enter)="enviarRapido()"
              placeholder="Tu pregunta...">
            <button 
              mat-icon-button 
              matSuffix 
              (click)="enviarRapido()"
              [disabled]="!preguntaRapida.trim() || enviandoRapido">
              <mat-icon>send</mat-icon>
            </button>
          </mat-form-field>
        </div>

        <!-- Botón para abrir chat completo -->
        <button mat-raised-button color="primary" (click)="irAlChatCompleto()" class="btn-chat-completo">
          💬 Abrir chat completo
        </button>
      </div>
    </div>
  `,
  styles: [`
    .chat-floating-container {
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 999;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .chat-float-button {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
      transition: all 0.3s ease;
      position: relative;

      .icon-robot {
        font-size: 28px;
        width: 28px;
        height: 28px;
      }

      .badge {
        position: absolute;
        top: -5px;
        right: -5px;
        font-size: 1.5rem;
        animation: pulse 2s infinite;
      }

      &:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
      }

      &.active {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
      }
    }

    .chat-panel {
      position: absolute;
      bottom: 80px;
      right: 0;
      width: 380px;
      max-height: 600px;
      background: white;
      border-radius: 12px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    .chat-panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;

      h3 {
        margin: 0;
        font-size: 1.1rem;
        font-weight: 600;
      }

      .close-btn {
        color: white;
      }
    }

    .chat-panel-messages {
      flex: 1;
      overflow-y: auto;
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      background: #f9f9f9;

      .mensaje {
        display: flex;
        flex-direction: column;
        gap: 4px;

        &.usuario {
          justify-content: flex-end;
        }

        .mensaje-bubble {
          max-width: 80%;
          padding: 8px 12px;
          border-radius: 8px;
          font-size: 0.9rem;
          line-height: 1.4;
          word-wrap: break-word;

          .usuario & {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
          }

          .ia & {
            background: white;
            color: #333;
            border: 1px solid #e0e0e0;
          }
        }

        .acciones-flotantes {
          display: flex;
          flex-direction: column;
          gap: 4px;
          max-width: 80%;
          margin-top: 4px;

          .btn-accion-flotante {
            font-size: 0.75rem;
            padding: 4px 8px;
            height: auto;
            min-height: 28px;
            display: flex;
            align-items: center;
            gap: 4px;
            justify-content: flex-start;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;

            mat-icon {
              font-size: 14px;
              width: 14px;
              height: 14px;
            }

            &:hover {
              background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
              transform: translateX(2px);
            }
          }
        }
      }

      &::-webkit-scrollbar {
        width: 6px;
      }

      &::-webkit-scrollbar-thumb {
        background: #ccc;
        border-radius: 3px;
      }
    }

    .chat-panel-input {
      padding: 12px;
      border-top: 1px solid #e0e0e0;
      background: white;

      .compact-input {
        width: 100%;

        input {
          font-size: 0.9rem;
        }
      }
    }

    .chat-panel-suggestions {
      padding: 0 12px 12px;
      background: #f2f5ff;
      display: flex;
      flex-direction: column;
      gap: 8px;

      .suggestion-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #4f46e5;
        font-weight: 600;
      }

      .suggestion-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }

      .suggestion-chip {
        padding: 6px 10px;
        border-radius: 18px;
        color: #1e293b;
        border: 1px solid rgba(102, 126, 234, 0.3);
        background: rgba(102, 126, 234, 0.08);
        font-size: 0.8rem;
        text-transform: none;
      }
    }

    .btn-chat-completo {
      width: calc(100% - 24px);
      margin: 0 12px 12px 12px;
      font-size: 0.85rem;
    }

    @keyframes pulse {
      0%, 100% {
        opacity: 1;
      }
      50% {
        opacity: 0.5;
      }
    }

    @media (max-width: 768px) {
      .chat-panel {
        width: calc(100vw - 48px);
        max-height: 70vh;
      }

      .chat-floating-container {
        bottom: 16px;
        right: 16px;
      }

      .chat-float-button {
        width: 56px;
        height: 56px;
      }
    }
  `]
})
export class ChatFloatingButtonComponent implements OnInit, OnDestroy {
  chatAbierto = false;
  preguntaRapida = '';
  enviandoRapido = false;
  mensajesCompacto: any[] = [];
  sugerencias: string[] = [];
  accionesActuales: any[] = [];  // ← NUEVO: Almacenar acciones
  private destroy$ = new Subject<void>();

  constructor(private chatService: ChatService) {}

  ngOnInit(): void {
    // Cargar sugerencias con contexto
    const contexto = this.chatService.obtenerContextoActual();
    this.cargarSugerencias(contexto);
  }

  cargarSugerencias(contexto: string): void {
    this.chatService.obtenerSugerencias(contexto)
      .pipe(takeUntil(this.destroy$))
      .subscribe(
        data => {
          this.sugerencias = data.sugerencias;
        },
        error => console.error('Error cargando sugerencias:', error)
      );
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  abrirChat(): void {
    this.chatAbierto = !this.chatAbierto;
    if (this.chatAbierto && this.mensajesCompacto.length === 0) {
      // Mensaje inicial
      this.mensajesCompacto = [{
        rol: 'ia',
        contenido: '¿Hola! ¿En qué puedo ayudarte? Escribe tu pregunta aquí.'
      }];
    }
  }

  usarSugerencia(sugerencia: string): void {
    this.preguntaRapida = sugerencia;
    this.enviarRapido();
  }

  cerrarChat(): void {
    this.chatAbierto = false;
  }

  enviarRapido(): void {
    if (!this.preguntaRapida.trim() || this.enviandoRapido) {
      return;
    }

    // Agregar pregunta del usuario
    this.mensajesCompacto.push({
      rol: 'usuario',
      contenido: this.preguntaRapida
    });

    const pregunta = this.preguntaRapida;
    this.preguntaRapida = '';
    this.enviandoRapido = true;

    // Obtener contexto actual
    const contexto = this.chatService.obtenerContextoActual();

    // Enviar al backend con contexto
    this.chatService.enviarPregunta(pregunta, contexto)
      .pipe(takeUntil(this.destroy$))
      .subscribe(
        (respuesta) => {
          // Mostrar solo las primeras líneas de la respuesta
          const lineas = respuesta.respuesta.split('\n');
          const resumenRespuesta = lineas.slice(0, 3).join('\n');

          this.mensajesCompacto.push({
            rol: 'ia',
            contenido: resumenRespuesta + (lineas.length > 3 ? '\n...' : ''),
            acciones: respuesta.acciones  // ← NUEVO: Almacenar acciones en el mensaje
          });

          // Guardar acciones actuales para mostrar botones
          this.accionesActuales = respuesta.acciones || [];

          this.enviandoRapido = false;

          // Auto scroll
          setTimeout(() => {
            const panel = document.querySelector('.chat-panel-messages');
            if (panel) {
              panel.scrollTop = panel.scrollHeight;
            }
          }, 100);
        },
        error => {
          console.error('Error:', error);
          this.mensajesCompacto.push({
            rol: 'ia',
            contenido: 'Lo siento, hubo un error. Abre el chat completo para más detalles.'
          });
          this.enviandoRapido = false;
        }
      );
  }

  irAlChatCompleto(): void {
    // Navegar al chat completo
    window.location.href = '/chat-ia';
  }

  ejecutarAccion(accion: any): void {
    if (accion.tipo === 'navegar' && accion.destino) {
      this.chatService.navegarA(accion.destino);
      return;
    }

    if (!accion.payload || !accion.entidad) {
      this.mensajesCompacto.push({
        rol: 'ia',
        contenido: 'Esta acción es una sugerencia. Abre el chat completo para ejecutarla con más detalles.'
      });
      return;
    }

    this.enviandoRapido = true;
    this.chatService.ejecutarAccion(accion)
      .pipe(takeUntil(this.destroy$))
      .subscribe(
        response => {
          const contenido = response.exitoso
            ? `✅ Acción ejecutada: ${response.mensaje}`
            : `⚠️ No se ejecutó la acción: ${response.mensaje}`;
          const detalles = response.faltan_campos ? `\nFaltan campos: ${response.faltan_campos.join(', ')}` : '';

          this.mensajesCompacto.push({
            rol: 'ia',
            contenido: contenido + detalles,
            tipo: response.exitoso ? 'accion' : 'error',
            informe: response.payload || response.resultado || null
          });
          this.enviandoRapido = false;
        },
        error => {
          console.error('Error ejecutando acción:', error);
          const detalle = error?.error?.detail || error?.message || 'Abre el chat completo para más información.';
          this.mensajesCompacto.push({
            rol: 'ia',
            contenido: `⚠️ No pude ejecutar la acción. ${detalle}`,
            tipo: 'error'
          });
          this.enviandoRapido = false;
        }
      );
  }

  navegarA(destino: string): void {
    this.chatService.navegarA(destino);
  }
}
