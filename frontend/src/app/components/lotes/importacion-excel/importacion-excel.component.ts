import { Component } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ApiService } from '../../../services/api.service';

@Component({
  selector: 'app-importacion-excel',
  templateUrl: './importacion-excel.component.html',
  styleUrls: ['./importacion-excel.component.scss']
})
export class ImportacionExcelComponent {
  selectedFile: File | null = null;
  uploading = false;

  constructor(
    private dialogRef: MatDialogRef<ImportacionExcelComponent>,
    private api: ApiService,
    private snackBar: MatSnackBar
  ) { }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
        this.selectedFile = file;
      } else {
        this.snackBar.open('Por favor seleccione un archivo Excel (.xlsx o .xls)', 'Cerrar', { duration: 3000 });
      }
    }
  }

  importar(): void {
    if (!this.selectedFile) {
      this.snackBar.open('Por favor seleccione un archivo', 'Cerrar', { duration: 3000 });
      return;
    }

    this.uploading = true;
    const formData = new FormData();
    formData.append('file', this.selectedFile);

    this.api.post('/importacion/excel/lotes', formData).subscribe({
      next: (response: any) => {
        this.uploading = false;
        this.snackBar.open(
          `Importación completada: ${response.lotes_creados} lotes creados${response.total_errores > 0 ? `, ${response.total_errores} errores` : ''}`,
          'Cerrar',
          { duration: 5000 }
        );
        if (response.errores && response.errores.length > 0) {
          console.warn('Errores durante la importación:', response.errores);
        }
        this.dialogRef.close(true);
      },
      error: (error) => {
        this.uploading = false;
        console.error('Error importando archivo:', error);
        const mensaje = error.error?.detail || error.message || 'Error al importar el archivo';
        this.snackBar.open(mensaje, 'Cerrar', { duration: 5000 });
      }
    });
  }

  cancelar(): void {
    this.dialogRef.close();
  }
}

