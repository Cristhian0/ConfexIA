import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CatalogoService } from '../../../services/catalogo.service';
import { Material, MaterialCreate, MaterialUpdate } from '../../../models/material.model';
import { MaterialDialogComponent } from './material-dialog.component';

@Component({
  selector: 'app-materiales',
  templateUrl: './materiales.component.html',
  styleUrls: ['./materiales.component.scss']
})
export class MaterialesComponent implements OnInit {
  materiales: Material[] = [];
  displayedColumns: string[] = ['codigo', 'nombre', 'descripcion', 'activo', 'acciones'];
  loading = false;

  constructor(
    private catalogoService: CatalogoService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) { }

  ngOnInit(): void {
    this.cargarMateriales();
  }

  cargarMateriales(): void {
    this.loading = true;
    this.catalogoService.listarMateriales().subscribe({
      next: (data) => {
        this.materiales = data;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error cargando materiales:', error);
        this.snackBar.open('Error al cargar materiales', 'Cerrar', { duration: 3000 });
        this.loading = false;
      }
    });
  }

  nuevoMaterial(): void {
    const dialogRef = this.dialog.open(MaterialDialogComponent, {
      width: '400px',
      data: {}
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.catalogoService.crearMaterial(result).subscribe({
          next: (material) => {
            this.snackBar.open('Material creado correctamente', 'Cerrar', { duration: 3000 });
            this.cargarMateriales();
          },
          error: (error) => {
            console.error('Error creando material:', error);
            this.snackBar.open('Error al crear material', 'Cerrar', { duration: 3000 });
          }
        });
      }
    });
  }

  editarMaterial(material: Material): void {
    const dialogRef = this.dialog.open(MaterialDialogComponent, {
      width: '400px',
      data: { material }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.catalogoService.actualizarMaterial(material.id, result).subscribe({
          next: (updatedMaterial) => {
            this.snackBar.open('Material actualizado correctamente', 'Cerrar', { duration: 3000 });
            this.cargarMateriales();
          },
          error: (error) => {
            console.error('Error actualizando material:', error);
            this.snackBar.open('Error al actualizar material', 'Cerrar', { duration: 3000 });
          }
        });
      }
    });
  }

  eliminarMaterial(material: Material): void {
    if (confirm(`¿Está seguro de eliminar el material "${material.nombre}"?`)) {
      this.catalogoService.eliminarMaterial(material.id).subscribe({
        next: () => {
          this.snackBar.open('Material eliminado correctamente', 'Cerrar', { duration: 3000 });
          this.cargarMateriales();
        },
        error: (error) => {
          console.error('Error eliminando material:', error);
          this.snackBar.open('Error al eliminar material', 'Cerrar', { duration: 3000 });
        }
      });
    }
  }
}

