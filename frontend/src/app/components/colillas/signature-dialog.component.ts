import { Component, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-signature-dialog',
  templateUrl: './signature-dialog.component.html',
  styleUrls: ['./signature-dialog.component.scss']
})
export class SignatureDialogComponent implements AfterViewInit {
  @ViewChild('canvas', { static: true }) canvas!: ElementRef<HTMLCanvasElement>;
  private ctx!: CanvasRenderingContext2D | null;
  private drawing = false;

  constructor(private dialogRef: MatDialogRef<SignatureDialogComponent>) {}

  ngAfterViewInit(): void {
    const c = this.canvas.nativeElement;
    c.width = c.offsetWidth * devicePixelRatio;
    c.height = 120 * devicePixelRatio;
    c.style.width = '100%';
    c.style.height = '120px';
    this.ctx = c.getContext('2d');
    if (this.ctx) {
      this.ctx.scale(devicePixelRatio, devicePixelRatio);
      this.ctx.lineWidth = 2;
      this.ctx.lineCap = 'round';
      this.ctx.strokeStyle = '#000';
    }
  }

  startDraw(event: MouseEvent | TouchEvent): void {
    this.drawing = true;
    const pos = this.getPos(event);
    if (this.ctx) this.ctx.beginPath(), this.ctx.moveTo(pos.x, pos.y);
  }

  moveDraw(event: MouseEvent | TouchEvent): void {
    if (!this.drawing) return;
    const pos = this.getPos(event);
    if (this.ctx) this.ctx.lineTo(pos.x, pos.y), this.ctx.stroke();
  }

  endDraw(): void {
    this.drawing = false;
  }

  getPos(event: any): { x: number; y: number } {
    const rect = this.canvas.nativeElement.getBoundingClientRect();
    const touch = event.touches ? event.touches[0] : null;
    const clientX = touch ? touch.clientX : event.clientX;
    const clientY = touch ? touch.clientY : event.clientY;
    return { x: clientX - rect.left, y: clientY - rect.top };
  }

  clear(): void {
    if (this.ctx) {
      const c = this.canvas.nativeElement;
      this.ctx.clearRect(0, 0, c.width, c.height);
    }
  }

  save(): void {
    const c = this.canvas.nativeElement;
    const dataUrl = c.toDataURL('image/png');
    this.dialogRef.close(dataUrl);
  }

  cancel(): void {
    this.dialogRef.close(null);
  }
}
