import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatExpansionPanel } from '@angular/material/expansion';
import { TallerService } from '../../services/taller.service';
import { Taller, Remision, EstadoRemision } from '../../models/taller.model';
import { TallerFormComponent } from './taller-form/taller-form.component';
import { RemisionFormComponent } from '../remisiones/remision-form/remision-form.component';

@Component({
  selector: 'app-talleres',
  templateUrl: './talleres.component.html',
  styleUrls: ['./talleres.component.scss']
})
export class TalleresComponent implements OnInit {
  talleres: Taller[] = [];
  remisionesPorTaller: { [tallerId: number]: Remision[] } = {};
  cargandoRemisiones: { [tallerId: number]: boolean } = {};
  loading = false;

  constructor(
    private tallerService: TallerService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) { }

  ngOnInit(): void {
    this.cargarTalleres();
  }

  cargarTalleres(): void {
    this.loading = true;
    this.tallerService.listar().subscribe({
      next: (data) => {
        this.talleres = data || [];
        this.loading = false;
      },
      error: (error) => {
        console.error('Error cargando talleres:', error);
        this.snackBar.open('Error al cargar talleres', 'Cerrar', { duration: 3000 });
        this.loading = false;
      }
    });
  }

  cargarRemisionesTaller(tallerId: number): void {
    if (this.remisionesPorTaller[tallerId]) {
      // Ya están cargadas
      return;
    }

    this.cargandoRemisiones[tallerId] = true;
    this.tallerService.listarRemisiones(tallerId).subscribe({
      next: (data) => {
        this.remisionesPorTaller[tallerId] = data || [];
        this.cargandoRemisiones[tallerId] = false;
      },
      error: (error) => {
        console.error(`Error cargando remisiones del taller ${tallerId}:`, error);
        this.remisionesPorTaller[tallerId] = [];
        this.cargandoRemisiones[tallerId] = false;
      }
    });
  }

  onPanelOpened(taller: Taller): void {
    // Cargar remisiones cuando se expande el panel
    this.cargarRemisionesTaller(taller.id);
  }

  abrirFormularioTaller(taller?: Taller): void {
    const dialogRef = this.dialog.open(TallerFormComponent, {
      width: '600px',
      maxWidth: '95vw',
      data: taller || null
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.cargarTalleres();
      }
    });
  }

  editarTaller(taller: Taller): void {
    this.abrirFormularioTaller(taller);
  }

  asignarTrabajo(taller: Taller): void {
    // Crear un objeto con el taller pre-seleccionado
    const dataWithTaller = {
      tallerPreSeleccionado: taller
    };
    
    const dialogRef = this.dialog.open(RemisionFormComponent, {
      width: '800px',
      maxWidth: '95vw',
      data: dataWithTaller // Pasar el taller pre-seleccionado
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        // Recargar remisiones de este taller
        delete this.remisionesPorTaller[taller.id];
        this.cargarRemisionesTaller(taller.id);
        this.snackBar.open('Remisión creada correctamente', 'Cerrar', { duration: 3000 });
      }
    });
  }

  verRemision(remision: Remision): void {
    const dialogRef = this.dialog.open(RemisionFormComponent, {
      width: '800px',
      maxWidth: '95vw',
      data: remision
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        // Recargar remisiones del taller asociado
        if (remision.taller_id) {
          delete this.remisionesPorTaller[remision.taller_id];
          this.cargarRemisionesTaller(remision.taller_id);
        }
      }
    });
  }

  editarRemision(remision: Remision): void {
    this.verRemision(remision);
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
    if (detalle.talla) {
      return detalle.talla.codigo || detalle.talla.nombre || `ID: ${detalle.talla_id}`;
    }
    return `Talla ID: ${detalle.talla_id}`;
  }

  getCantidadRemisiones(tallerId: number): number {
    return this.remisionesPorTaller[tallerId]?.length || 0;
  }
}

