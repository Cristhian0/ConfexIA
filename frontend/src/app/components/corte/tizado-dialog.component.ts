import { Component, Inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { CorteService, OrdenCorte, OrdenCorteUpdateTizado } from '../../services/corte.service';

@Component({
  selector: 'app-tizado-dialog',
  template: `
    <h2 mat-dialog-title>Registrar Tizado - Orden {{ data.orden.numero_orden }}</h2>
    <mat-dialog-content>
      <form [formGroup]="form" class="dialog-form">
        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Metros de tela utilizados en tizado</mat-label>
          <input matInput type="number" formControlName="metros_tizado" step="0.01" min="0">
          <span matSuffix>m</span>
        </mat-form-field>

        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Rendimiento (%)</mat-label>
          <input matInput type="number" formControlName="rendimiento_pct" min="0" max="100">
          <span matSuffix>%</span>
        </mat-form-field>
      </form>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button (click)="cancelar()">Cancelar</button>
      <button mat-raised-button color="primary" (click)="guardar()" [disabled]="form.invalid">
        Registrar Tizado
      </button>
    </mat-dialog-actions>
  `,
  styles: [`
    .dialog-form {
      display: flex;
      flex-direction: column;
      gap: 16px;
      min-width: 400px;
      padding: 16px 0;
    }
    .full-width {
      width: 100%;
    }
  `]
})
export class TizadoDialogComponent {
  form: FormGroup;

  constructor(
    private fb: FormBuilder,
    private corteService: CorteService,
    private dialogRef: MatDialogRef<TizadoDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { orden: OrdenCorte }
  ) {
    this.form = this.fb.group({
      metros_tizado: [data.orden.metros_tizado || 0, [Validators.required, Validators.min(0.01)]],
      rendimiento_pct: [data.orden.rendimiento_pct || 0, [Validators.required, Validators.min(0), Validators.max(100)]]
    });
  }

  cancelar(): void {
    this.dialogRef.close();
  }

  guardar(): void {
    if (this.form.invalid) return;

    const data: OrdenCorteUpdateTizado = this.form.value;
    this.corteService.registrarTizado(this.data.orden.id, data).subscribe({
      next: (ordenActualizada) => {
        this.dialogRef.close(ordenActualizada);
      },
      error: (error) => {
        console.error('Error registrando tizado:', error);
        alert('Error al registrar tizado');
      }
    });
  }
}