import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CatalogoService } from '../../../services/catalogo.service';
import { Talla, TallaCreate, TallaUpdate } from '../../../models/talla.model';
import { TallaDialogComponent } from './talla-dialog.component';

@Component({
  selector: 'app-tallas',
  templateUrl: './tallas.component.html',
  styleUrls: ['./tallas.component.scss']
})
export class TallasComponent implements OnInit {
  tallas: Talla[] = [];
  displayedColumns: string[] = ['codigo', 'nombre', 'activo', 'acciones'];
  loading = false;

  constructor(
    private catalogoService: CatalogoService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) { }

  ngOnInit(): void {
    this.cargarTallas();
  }

  cargarTallas(): void {
    this.loading = true;
    this.catalogoService.listarTallas().subscribe({
      next: (data) => {
        this.tallas = data;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error cargando tallas:', error);
        this.snackBar.open('Error al cargar tallas', 'Cerrar', { duration: 3000 });
        this.loading = false;
      }
    });
  }

  nuevaTalla(): void {
    const dialogRef = this.dialog.open(TallaDialogComponent, {
      width: '400px',
      data: {}
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.catalogoService.crearTalla(result).subscribe({
          next: (talla) => {
            this.snackBar.open('Talla creada correctamente', 'Cerrar', { duration: 3000 });
            this.cargarTallas();
          },
          error: (error) => {
            console.error('Error creando talla:', error);
            this.snackBar.open('Error al crear talla', 'Cerrar', { duration: 3000 });
          }
        });
      }
    });
  }

  editarTalla(talla: Talla): void {
    const dialogRef = this.dialog.open(TallaDialogComponent, {
      width: '400px',
      data: { talla }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.catalogoService.actualizarTalla(talla.id, result).subscribe({
          next: (updatedTalla) => {
            this.snackBar.open('Talla actualizada correctamente', 'Cerrar', { duration: 3000 });
            this.cargarTallas();
          },
          error: (error) => {
            console.error('Error actualizando talla:', error);
            this.snackBar.open('Error al actualizar talla', 'Cerrar', { duration: 3000 });
          }
        });
      }
    });
  }

  eliminarTalla(talla: Talla): void {
    if (confirm(`¿Está seguro de eliminar la talla "${talla.nombre}"?`)) {
      this.catalogoService.eliminarTalla(talla.id).subscribe({
        next: () => {
          this.snackBar.open('Talla eliminada correctamente', 'Cerrar', { duration: 3000 });
          this.cargarTallas();
        },
        error: (error) => {
          console.error('Error eliminando talla:', error);
          this.snackBar.open('Error al eliminar talla', 'Cerrar', { duration: 3000 });
        }
      });
    }
  }
}
