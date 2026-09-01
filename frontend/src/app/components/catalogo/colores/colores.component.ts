import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CatalogoService } from '../../../services/catalogo.service';
import { Color, ColorCreate, ColorUpdate } from '../../../models/color.model';
import { ColorDialogComponent } from './color-dialog.component';

@Component({
  selector: 'app-colores',
  templateUrl: './colores.component.html',
  styleUrls: ['./colores.component.scss']
})
export class ColoresComponent implements OnInit {
  colores: Color[] = [];
  displayedColumns: string[] = ['codigo', 'nombre', 'color_hex', 'activo', 'acciones'];
  loading = false;

  constructor(
    private catalogoService: CatalogoService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) { }

  ngOnInit(): void {
    this.cargarColores();
  }

  cargarColores(): void {
    this.loading = true;
    this.catalogoService.listarColores().subscribe({
      next: (data) => {
        this.colores = data;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error cargando colores:', error);
        this.snackBar.open('Error al cargar colores', 'Cerrar', { duration: 3000 });
        this.loading = false;
      }
    });
  }

  nuevoColor(): void {
    const dialogRef = this.dialog.open(ColorDialogComponent, {
      width: '400px',
      data: {}
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.catalogoService.crearColor(result).subscribe({
          next: (color) => {
            this.snackBar.open('Color creado correctamente', 'Cerrar', { duration: 3000 });
            this.cargarColores();
          },
          error: (error) => {
            console.error('Error creando color:', error);
            this.snackBar.open('Error al crear color', 'Cerrar', { duration: 3000 });
          }
        });
      }
    });
  }

  editarColor(color: Color): void {
    const dialogRef = this.dialog.open(ColorDialogComponent, {
      width: '400px',
      data: { color }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.catalogoService.actualizarColor(color.id, result).subscribe({
          next: (updatedColor) => {
            this.snackBar.open('Color actualizado correctamente', 'Cerrar', { duration: 3000 });
            this.cargarColores();
          },
          error: (error) => {
            console.error('Error actualizando color:', error);
            this.snackBar.open('Error al actualizar color', 'Cerrar', { duration: 3000 });
          }
        });
      }
    });
  }

  eliminarColor(color: Color): void {
    if (confirm(`¿Está seguro de eliminar el color "${color.nombre}"?`)) {
      this.catalogoService.eliminarColor(color.id).subscribe({
        next: () => {
          this.snackBar.open('Color eliminado correctamente', 'Cerrar', { duration: 3000 });
          this.cargarColores();
        },
        error: (error) => {
          console.error('Error eliminando color:', error);
          this.snackBar.open('Error al eliminar color', 'Cerrar', { duration: 3000 });
        }
      });
    }
  }
}

