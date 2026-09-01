import { Component, Inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { CorteService, OrdenCorte, OrdenCorteUpdateSobrantes } from '../../services/corte.service';

@Component({
  selector: 'app-sobrantes-dialog',
  template: `
    <h2 mat-dialog-title>Registrar Sobrantes - Orden {{ data.orden.numero_orden }}</h2>
    <mat-dialog-content>
      <form [formGroup]="form" class="dialog-form">
        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Metros de sobrante</mat-label>
          <input matInput type="number" formControlName="metros_sobrante" step="0.01" min="0">
          <span matSuffix>m</span>
        </mat-form-field>

        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Metros de desperdicio</mat-label>
          <input matInput type="number" formControlName="metros_desperdicio" step="0.01" min="0">
          <span matSuffix>m</span>
        </mat-form-field>
      </form>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button (click)="cancelar()">Cancelar</button>
      <button mat-raised-button color="primary" (click)="guardar()" [disabled]="form.invalid">
        Registrar Sobrantes
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
export class SobrantesDialogComponent {
  form: FormGroup;

  constructor(
    private fb: FormBuilder,
    private corteService: CorteService,
    private dialogRef: MatDialogRef<SobrantesDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { orden: OrdenCorte }
  ) {
    this.form = this.fb.group({
      metros_sobrante: [data.orden.metros_sobrante || 0, [Validators.min(0)]],
      metros_desperdicio: [data.orden.metros_desperdicio || 0, [Validators.min(0)]]
    });
  }

  cancelar(): void {
    this.dialogRef.close();
  }

  guardar(): void {
    if (this.form.invalid) return;

    const data: OrdenCorteUpdateSobrantes = this.form.value;
    this.corteService.registrarSobrantes(this.data.orden.id, data).subscribe({
      next: (ordenActualizada) => {
        this.dialogRef.close(ordenActualizada);
      },
      error: (error) => {
        console.error('Error registrando sobrantes:', error);
        alert('Error al registrar sobrantes');
      }
    });
  }
}