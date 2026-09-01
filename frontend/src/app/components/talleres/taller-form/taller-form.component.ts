import { Component, OnInit, Inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { TallerService } from '../../../services/taller.service';
import { Taller, TallerCreate } from '../../../models/taller.model';

@Component({
  selector: 'app-taller-form',
  templateUrl: './taller-form.component.html',
  styleUrls: ['./taller-form.component.scss']
})
export class TallerFormComponent implements OnInit {
  form: FormGroup;
  isEdit = false;

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<TallerFormComponent>,
    @Inject(MAT_DIALOG_DATA) public data: Taller | null,
    private tallerService: TallerService,
    private snackBar: MatSnackBar
  ) {
    this.form = this.fb.group({
      codigo: ['', Validators.required],
      nombre: ['', Validators.required],
      direccion: [''],
      telefono: [''],
      contacto: [''],
      activo: [true],
      capacidad_diaria: [0, [Validators.required, Validators.min(0)]]
    });
  }

  ngOnInit(): void {
    if (this.data) {
      this.isEdit = true;
      this.form.patchValue(this.data);
    }
  }

  guardar(): void {
    if (this.form.valid) {
      const formValue = this.form.value;
      const tallerData: TallerCreate = {
        codigo: formValue.codigo,
        nombre: formValue.nombre,
        direccion: formValue.direccion || '',
        telefono: formValue.telefono || '',
        contacto: formValue.contacto || '',
        activo: formValue.activo !== false,
        capacidad_diaria: parseInt(formValue.capacidad_diaria, 10) || 0
      };

      if (this.isEdit && this.data) {
        this.tallerService.actualizar(this.data.id, tallerData).subscribe({
          next: () => {
            this.snackBar.open('Taller actualizado correctamente', 'Cerrar', { duration: 3000 });
            this.dialogRef.close(true);
          },
          error: (error) => {
            console.error('Error actualizando taller:', error);
            const mensaje = error.error?.detail || error.message || 'Error al actualizar taller';
            this.snackBar.open(mensaje, 'Cerrar', { duration: 5000 });
          }
        });
      } else {
        this.tallerService.crear(tallerData).subscribe({
          next: () => {
            this.snackBar.open('Taller creado correctamente', 'Cerrar', { duration: 3000 });
            this.dialogRef.close(true);
          },
          error: (error) => {
            console.error('Error creando taller:', error);
            const mensaje = error.error?.detail || error.message || 'Error al crear taller';
            this.snackBar.open(mensaje, 'Cerrar', { duration: 5000 });
          }
        });
      }
    } else {
      this.snackBar.open('Por favor complete todos los campos requeridos', 'Cerrar', { duration: 3000 });
    }
  }

  cancelar(): void {
    this.dialogRef.close();
  }
}
