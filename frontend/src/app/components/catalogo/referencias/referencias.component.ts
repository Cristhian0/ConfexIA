import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CatalogoService } from '../../../services/catalogo.service';
import { Referencia, ReferenciaCreate, ReferenciaUpdate } from '../../../models/referencia.model';
import { ReferenciaDialogComponent } from './referencia-dialog.component';

@Component({
  selector: 'app-referencias',
  templateUrl: './referencias.component.html',
  styleUrls: ['./referencias.component.scss']
})
export class ReferenciasComponent implements OnInit {
  referencias: Referencia[] = [];
  displayedColumns: string[] = ['codigo', 'nombre', 'descripcion', 'es_pedido_especial', 'activo', 'acciones'];
  loading = false;

  constructor(
    private catalogoService: CatalogoService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) { }

  ngOnInit(): void {
    this.cargarReferencias();
  }

  cargarReferencias(): void {
    this.loading = true;
    this.catalogoService.listarReferencias().subscribe({
      next: (data) => {
        this.referencias = data;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error cargando referencias:', error);
        this.snackBar.open('Error al cargar referencias', 'Cerrar', { duration: 3000 });
        this.loading = false;
      }
    });
  }

  nuevaReferencia(): void {
    const dialogRef = this.dialog.open(ReferenciaDialogComponent, {
      width: '400px',
      data: {}
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.catalogoService.crearReferencia(result).subscribe({
          next: (referencia) => {
            this.snackBar.open('Referencia creada correctamente', 'Cerrar', { duration: 3000 });
            this.cargarReferencias();
          },
          error: (error) => {
            console.error('Error creando referencia:', error);
            this.snackBar.open('Error al crear referencia', 'Cerrar', { duration: 3000 });
          }
        });
      }
    });
  }

  editarReferencia(referencia: Referencia): void {
    const dialogRef = this.dialog.open(ReferenciaDialogComponent, {
      width: '400px',
      data: { referencia }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.catalogoService.actualizarReferencia(referencia.id, result).subscribe({
          next: (updatedReferencia) => {
            this.snackBar.open('Referencia actualizada correctamente', 'Cerrar', { duration: 3000 });
            this.cargarReferencias();
          },
          error: (error) => {
            console.error('Error actualizando referencia:', error);
            this.snackBar.open('Error al actualizar referencia', 'Cerrar', { duration: 3000 });
          }
        });
      }
    });
  }

  eliminarReferencia(referencia: Referencia): void {
    if (confirm(`¿Está seguro de eliminar la referencia "${referencia.nombre}"?`)) {
      this.catalogoService.eliminarReferencia(referencia.id).subscribe({
        next: () => {
          this.snackBar.open('Referencia eliminada correctamente', 'Cerrar', { duration: 3000 });
          this.cargarReferencias();
        },
        error: (error) => {
          console.error('Error eliminando referencia:', error);
          this.snackBar.open('Error al eliminar referencia', 'Cerrar', { duration: 3000 });
        }
      });
    }
  }
}

