import { Component, Inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { CorteService, OrdenCorte, OrdenCorteUpdateCorte } from '../../services/corte.service';

@Component({
  selector: 'app-corte-dialog',
  template: `
    <h2 mat-dialog-title>Registrar Corte - Orden {{ data.orden.numero_orden }}</h2>
    <mat-dialog-content>
      <form [formGroup]="form" class="dialog-form">
        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Número de piezas cortadas</mat-label>
          <input matInput type="number" formControlName="piezas_cortadas" min="0">
        </mat-form-field>

        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Capas utilizadas</mat-label>
          <input matInput type="number" formControlName="capas_utilizadas" min="1">
        </mat-form-field>
      </form>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button (click)="cancelar()">Cancelar</button>
      <button mat-raised-button color="primary" (click)="guardar()" [disabled]="form.invalid">
        Registrar Corte
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
export class CorteDialogComponent {
  form: FormGroup;

  constructor(
    private fb: FormBuilder,
    private corteService: CorteService,
    private dialogRef: MatDialogRef<CorteDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { orden: OrdenCorte }
  ) {
    this.form = this.fb.group({
      piezas_cortadas: [data.orden.piezas_cortadas || 0, [Validators.required, Validators.min(0)]],
      capas_utilizadas: [data.orden.capas_utilizadas || 0, [Validators.required, Validators.min(1)]]
    });
  }

  cancelar(): void {
    this.dialogRef.close();
  }

  guardar(): void {
    if (this.form.invalid) return;

    const data: OrdenCorteUpdateCorte = this.form.value;
    this.corteService.registrarCorte(this.data.orden.id, data).subscribe({
      next: (ordenActualizada) => {
        this.dialogRef.close(ordenActualizada);
      },
      error: (error) => {
        console.error('Error registrando corte:', error);
        alert('Error al registrar corte');
      }
    });
  }
}