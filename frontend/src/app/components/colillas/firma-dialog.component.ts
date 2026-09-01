import { AfterViewInit, Component, ElementRef, ViewChild } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-firma-dialog',
  template: `
    <h2 mat-dialog-title>Firma de la Colilla</h2>
    <mat-dialog-content>
      <p>Firma en el recuadro y luego presiona Guardar para adjuntar la firma al PDF de la colilla.</p>
      <div class="canvas-wrapper">
        <canvas
          #signatureCanvas
          (mousedown)="startDrawing($event)"
          (mousemove)="draw($event)"
          (mouseup)="endDrawing()"
          (mouseleave)="endDrawing()"
          (touchstart)="startDrawing($event)"
          (touchmove)="draw($event)"
          (touchend)="endDrawing()"
        ></canvas>
      </div>
      <div class="canvas-actions">
        <button mat-button type="button" (click)="limpiar()">Limpiar</button>
        <span class="hint">Firma obligatoria para generar el PDF</span>
      </div>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button type="button" (click)="cancelar()">Cancelar</button>
      <button mat-raised-button color="primary" type="button" (click)="guardar()" [disabled]="!firmado">
        Guardar firma
      </button>
    </mat-dialog-actions>
  `,
  styles: [
    `
      .canvas-wrapper {
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        overflow: hidden;
        background: #ffffff;
        width: 100%;
        min-height: 180px;
      }

      canvas {
        width: 100%;
        height: 180px;
        touch-action: none;
      }

      .canvas-actions {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 12px;
      }

      .hint {
        color: #475569;
        font-size: 13px;
      }
    `
  ]
})
export class FirmaDialogComponent implements AfterViewInit {
  @ViewChild('signatureCanvas', { static: false }) canvasRef!: ElementRef<HTMLCanvasElement>;
  firmado = false;
  private ctx: CanvasRenderingContext2D | null = null;
  private drawing = false;
  private lastX = 0;
  private lastY = 0;
  private readonly dpr = window.devicePixelRatio || 1;

  constructor(private dialogRef: MatDialogRef<FirmaDialogComponent>) {}

  ngAfterViewInit(): void {
    const canvas = this.canvasRef.nativeElement;
    const width = canvas.offsetWidth;
    const height = 180;
    canvas.width = width * this.dpr;
    canvas.height = height * this.dpr;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    this.ctx = canvas.getContext('2d');
    if (this.ctx) {
      this.ctx.scale(this.dpr, this.dpr);
      this.ctx.strokeStyle = '#000000';
      this.ctx.lineWidth = 2;
      this.ctx.lineCap = 'round';
      this.ctx.lineJoin = 'round';
    }
  }

  private getPointerPosition(event: MouseEvent | TouchEvent): { x: number; y: number } {
    const canvas = this.canvasRef.nativeElement;
    const rect = canvas.getBoundingClientRect();

    if ((event as TouchEvent).touches && (event as TouchEvent).touches.length) {
      const touch = (event as TouchEvent).touches[0];
      return {
        x: touch.clientX - rect.left,
        y: touch.clientY - rect.top
      };
    }

    const mouseEvent = event as MouseEvent;
    return {
      x: mouseEvent.clientX - rect.left,
      y: mouseEvent.clientY - rect.top
    };
  }

  startDrawing(event: MouseEvent | TouchEvent): void {
    event.preventDefault();
    if (!this.ctx) {
      return;
    }
    this.drawing = true;
    const point = this.getPointerPosition(event);
    this.lastX = point.x;
    this.lastY = point.y;
  }

  draw(event: MouseEvent | TouchEvent): void {
    if (!this.drawing || !this.ctx) {
      return;
    }
    event.preventDefault();
    const point = this.getPointerPosition(event);
    this.ctx.beginPath();
    this.ctx.moveTo(this.lastX, this.lastY);
    this.ctx.lineTo(point.x, point.y);
    this.ctx.stroke();
    this.lastX = point.x;
    this.lastY = point.y;
    this.firmado = true;
  }

  endDrawing(): void {
    this.drawing = false;
  }

  limpiar(): void {
    if (!this.ctx) {
      return;
    }
    const canvas = this.canvasRef.nativeElement;
    this.ctx.clearRect(0, 0, canvas.width, canvas.height);
    this.firmado = false;
  }

  cancelar(): void {
    this.dialogRef.close();
  }

  guardar(): void {
    if (!this.firmado) {
      return;
    }
    const canvas = this.canvasRef.nativeElement;
    const firmaBase64 = canvas.toDataURL('image/png');
    this.dialogRef.close(firmaBase64);
  }
}
