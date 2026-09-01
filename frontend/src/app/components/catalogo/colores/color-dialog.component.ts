import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Color, ColorCreate, ColorUpdate } from '../../../models/color.model';

@Component({
  selector: 'app-color-dialog',
  templateUrl: './color-dialog.component.html',
  styleUrls: ['./color-dialog.component.scss']
})
export class ColorDialogComponent {
  colorForm: FormGroup;
  isEdit = false;

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<ColorDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { color?: Color }
  ) {
    this.isEdit = !!data.color;
    this.colorForm = this.fb.group({
      codigo: [data.color?.codigo || '', [Validators.required, Validators.maxLength(20)]],
      nombre: [data.color?.nombre || '', [Validators.required, Validators.maxLength(100)]],
      color_hex: [data.color?.color_hex || '#000000'],
      activo: [data.color?.activo ?? true]
    });
  }

  onSubmit(): void {
    if (this.colorForm.valid) {
      const formValue = this.colorForm.value;
      if (this.isEdit) {
        const updateData: ColorUpdate = {
          codigo: formValue.codigo,
          nombre: formValue.nombre,
          color_hex: formValue.color_hex,
          activo: formValue.activo
        };
        this.dialogRef.close(updateData);
      } else {
        const createData: ColorCreate = {
          codigo: formValue.codigo,
          nombre: formValue.nombre,
          color_hex: formValue.color_hex,
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