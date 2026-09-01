import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Referencia, ReferenciaCreate, ReferenciaUpdate } from '../../../models/referencia.model';

@Component({
  selector: 'app-referencia-dialog',
  templateUrl: './referencia-dialog.component.html',
  styleUrls: ['./referencia-dialog.component.scss']
})
export class ReferenciaDialogComponent {
  referenciaForm: FormGroup;
  isEdit = false;

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<ReferenciaDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { referencia?: Referencia }
  ) {
    this.isEdit = !!data.referencia;
    this.referenciaForm = this.fb.group({
      codigo: [data.referencia?.codigo || '', [Validators.required, Validators.maxLength(20)]],
      nombre: [data.referencia?.nombre || '', [Validators.required, Validators.maxLength(200)]],
      descripcion: [data.referencia?.descripcion || '', Validators.maxLength(500)],
      es_pedido_especial: [data.referencia?.es_pedido_especial ?? false],
      activo: [data.referencia?.activo ?? true]
    });
  }

  onSubmit(): void {
    if (this.referenciaForm.valid) {
      const formValue = this.referenciaForm.value;
      if (this.isEdit) {
        const updateData: ReferenciaUpdate = {
          codigo: formValue.codigo,
          nombre: formValue.nombre,
          descripcion: formValue.descripcion,
          es_pedido_especial: formValue.es_pedido_especial,
          activo: formValue.activo
        };
        this.dialogRef.close(updateData);
      } else {
        const createData: ReferenciaCreate = {
          codigo: formValue.codigo,
          nombre: formValue.nombre,
          descripcion: formValue.descripcion,
          es_pedido_especial: formValue.es_pedido_especial,
          activo: formValue.activo
        };
        this.dialogRef.close(createData);
      }
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}