import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Talla, TallaCreate, TallaUpdate } from '../../../models/talla.model';

@Component({
  selector: 'app-talla-dialog',
  templateUrl: './talla-dialog.component.html',
  styleUrls: ['./talla-dialog.component.scss']
})
export class TallaDialogComponent {
  tallaForm: FormGroup;
  isEdit = false;

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<TallaDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { talla?: Talla }
  ) {
    this.isEdit = !!data.talla;
    this.tallaForm = this.fb.group({
      codigo: [data.talla?.codigo || '', [Validators.required, Validators.maxLength(20)]],
      nombre: [data.talla?.nombre || '', [Validators.required, Validators.maxLength(100)]],
      activo: [data.talla?.activo ?? true]
    });
  }

  onSubmit(): void {
    if (this.tallaForm.valid) {
      const formValue = this.tallaForm.value;
      if (this.isEdit) {
        const updateData: TallaUpdate = {
          codigo: formValue.codigo,
          nombre: formValue.nombre,
          activo: formValue.activo
        };
        this.dialogRef.close(updateData);
      } else {
        const createData: TallaCreate = {
          codigo: formValue.codigo,
          nombre: formValue.nombre,
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