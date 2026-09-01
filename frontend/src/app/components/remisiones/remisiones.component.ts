import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { TallerService } from '../../services/taller.service';
import { Remision, EstadoRemision } from '../../models/taller.model';
import { RemisionFormComponent } from './remision-form/remision-form.component';

@Component({
  selector: 'app-remisiones',
  templateUrl: './remisiones.component.html',
  styleUrls: ['./remisiones.component.scss']
})
export class RemisionesComponent implements OnInit {
  remisiones: Remision[] = [];
  loading = false;
  columnas: string[] = ['numero_remision', 'taller', 'lote', 'detalles', 'estado', 'fechas', 'acciones'];

  constructor(
    private tallerService: TallerService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) { }

  ngOnInit(): void {
    this.cargarRemisiones();
  }

  cargarRemisiones(): void {
    this.loading = true;
    this.tallerService.listarRemisiones().subscribe({
      next: (data) => {
        this.remisiones = data || [];
        this.loading = false;
      },
      error: (error) => {
        console.error('Error cargando remisiones:', error);
        this.snackBar.open('Error al cargar remisiones', 'Cerrar', { duration: 3000 });
        this.loading = false;
      }
    });
  }

  abrirFormulario(remision?: Remision): void {
    const dialogRef = this.dialog.open(RemisionFormComponent, {
      width: '800px',
      maxWidth: '95vw',
      data: remision || null
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.cargarRemisiones();
      }
    });
  }

  verDetalles(remision: Remision): void {
    // Por ahora, abrir el formulario en modo solo lectura o crear un componente de detalles
    this.abrirFormulario(remision);
  }

  editar(remision: Remision): void {
    this.abrirFormulario(remision);
  }

  getEstadoLabel(estado: EstadoRemision): string {
    const estados: { [key: string]: string } = {
      'pendiente': 'Pendiente',
      'en_transito': 'En Tránsito',
      'recibida': 'Recibida',
      'parcialmente_entregada': 'Parcialmente Entregada',
      'completada': 'Completada',
      'cancelada': 'Cancelada'
    };
    return estados[estado] || estado;
  }

  formatDate(date: string | null | undefined): string {
    if (!date) return '-';
    try {
      const d = new Date(date);
      return d.toLocaleDateString('es-ES', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return date;
    }
  }

  getTallaNombre(detalle: any): string {
    // Si el detalle tiene la relación de talla cargada
    if (detalle.talla) {
      return detalle.talla.codigo || detalle.talla.nombre || `ID: ${detalle.talla_id}`;
    }
    // Fallback al ID si no hay relación
    return `Talla ID: ${detalle.talla_id}`;
  }
}

