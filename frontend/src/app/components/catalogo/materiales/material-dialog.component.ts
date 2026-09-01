import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Material, MaterialCreate, MaterialUpdate } from '../../../models/material.model';

@Component({
  selector: 'app-material-dialog',
  templateUrl: './material-dialog.component.html',
  styleUrls: ['./material-dialog.component.scss']
})
export class MaterialDialogComponent {
  materialForm: FormGroup;
  isEdit = false;

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<MaterialDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { material?: Material }
  ) {
    this.isEdit = !!data.material;
    this.materialForm = this.fb.group({
      codigo: [data.material?.codigo || '', [Validators.required, Validators.maxLength(20)]],
      nombre: [data.material?.nombre || '', [Validators.required, Validators.maxLength(100)]],
      descripcion: [data.material?.descripcion || '', Validators.maxLength(200)],
      activo: [data.material?.activo ?? true]
    });
  }

  onSubmit(): void {
    if (this.materialForm.valid) {
      const formValue = this.materialForm.value;
      if (this.isEdit) {
        const updateData: MaterialUpdate = {
          codigo: formValue.codigo,
          nombre: formValue.nombre,
          descripcion: formValue.descripcion,
          activo: formValue.activo
        };
        this.dialogRef.close(updateData);
      } else {
        const createData: MaterialCreate = {
          codigo: formValue.codigo,
          nombre: formValue.nombre,
          descripcion: formValue.descripcion,
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