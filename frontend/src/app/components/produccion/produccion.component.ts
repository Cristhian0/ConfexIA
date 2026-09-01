import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ProduccionService } from '../../services/produccion.service';
import { LoteService } from '../../services/lote.service';
import { OrdenProduccion, EstadoOrdenProduccion, TipoOperacion, RegistroProduccion } from '../../models/produccion.model';
import { Lote } from '../../models/lote.model';

@Component({
  selector: 'app-produccion',
  templateUrl: './produccion.component.html',
  styleUrls: ['./produccion.component.scss']
})
export class ProduccionComponent implements OnInit {
  // Listas principales
  ordenesProduccion: OrdenProduccion[] = [];
  lotesDisponibles: Lote[] = [];

  // Formularios
  formNuevaOrden: FormGroup;
  formRegistroProduccion: FormGroup;
  formCalidadOrden: FormGroup;

  // Estados y controles
  loading = false;
  ordenSeleccionada: OrdenProduccion | null = null;
  registrosSeleccionados: RegistroProduccion[] = [];

  // UI
  displayedColumns: string[] = ['numero_orden', 'numero_lote', 'referencia', 'estado', 'fecha_creacion', 'fecha_fin', 'registros', 'acciones'];
  estadoPagoOptions: string[] = ['Pagado', 'Pendiente', 'Atrasado'];
  estadoOrdenLabels: { [key in EstadoOrdenProduccion]: string } = {
    [EstadoOrdenProduccion.PENDIENTE]: 'Pendiente',
    [EstadoOrdenProduccion.EN_PROGRESO]: 'En Progreso',
    [EstadoOrdenProduccion.COMPLETADA]: 'Completada',
    [EstadoOrdenProduccion.CANCELADA]: 'Cancelada'
  };

  operacionesLabels: { [key in TipoOperacion]: string } = {
    [TipoOperacion.ENSAMBLE]: 'Ensamble',
    [TipoOperacion.COSTURA]: 'Costura',
    [TipoOperacion.FILETEADO]: 'Fileteado',
    [TipoOperacion.TERMINACION]: 'Terminación'
  };

  constructor(
    private produccionService: ProduccionService,
    private loteService: LoteService,
    private fb: FormBuilder,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {
    this.formNuevaOrden = this.fb.group({
      lote_id: ['', Validators.required],
      observaciones: ['']
    });

    this.formRegistroProduccion = this.fb.group({
      operacion: ['', Validators.required],
      operario: ['', Validators.required],
      linea_produccion: [''],
      cantidad_producida: [0, [Validators.required, Validators.min(0)]],
      cantidad_rechazada: [0, [Validators.min(0)]],
      tiempo_inicio: ['', Validators.required],
      tiempo_fin: [''],
      notas: ['']
    });

    this.formCalidadOrden = this.fb.group({
      fecha_recepcion: [''],
      revisado_por: [''],
      cantidad_parcial: [0, [Validators.min(0)]],
      cantidad_arreglos: [0, [Validators.min(0)]],
      cantidad_imperfecciones: [0, [Validators.min(0)]],
      cantidad_pendiente: [0, [Validators.min(0)]],
      requiere_compras: [false],
      fecha_entrega_total: [''],
      dias_mora: [0, [Validators.min(0)]],
      estado_pago: ['']
    });
  }

  ngOnInit(): void {
    this.cargarDatos();
  }

  cargarDatos(): void {
    this.loading = true;
    
    // Cargar órdenes de producción
    this.produccionService.listarOrdenes().subscribe({
      next: (ordenes) => {
        this.ordenesProduccion = ordenes;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error cargando órdenes:', error);
        this.snackBar.open('Error al cargar órdenes', 'Cerrar', { duration: 3000 });
        this.loading = false;
      }
    });

    // Cargar lotes disponibles
    this.loteService.listar().subscribe({
      next: (lotes) => {
        this.lotesDisponibles = lotes;
      },
      error: (error) => {
        console.error('Error cargando lotes:', error);
      }
    });
  }

  /**
   * RF-11: Crear nueva orden de confección
   */
  crearOrdenProduccion(): void {
    if (this.formNuevaOrden.invalid) {
      this.snackBar.open('Por favor completa los campos requeridos', 'Cerrar', { duration: 3000 });
      return;
    }

    const datos = this.formNuevaOrden.value;
    this.produccionService.crearOrden(datos).subscribe({
      next: (nuevaOrden) => {
        this.ordenesProduccion.unshift(nuevaOrden);
        this.formNuevaOrden.reset();
        this.snackBar.open('Orden de producción creada exitosamente', 'Cerrar', { duration: 3000 });
      },
      error: (error) => {
        console.error('Error creando orden:', error);
        this.snackBar.open('Error al crear orden de producción', 'Cerrar', { duration: 3000 });
      }
    });
  }

  /**
   * Seleccionar una orden para ver detalles
   */
  seleccionarOrden(orden: OrdenProduccion): void {
    this.ordenSeleccionada = orden;
    this.formCalidadOrden.patchValue({
      fecha_recepcion: orden.fecha_recepcion || '',
      revisado_por: orden.revisado_por || '',
      cantidad_parcial: orden.cantidad_parcial ?? 0,
      cantidad_arreglos: orden.cantidad_arreglos ?? 0,
      cantidad_imperfecciones: orden.cantidad_imperfecciones ?? 0,
      cantidad_pendiente: orden.cantidad_pendiente ?? 0,
      requiere_compras: !!orden.requiere_compras,
      fecha_entrega_total: orden.fecha_entrega_total || '',
      dias_mora: orden.dias_mora ?? 0,
      estado_pago: orden.estado_pago || ''
    });
    if (orden.registros_produccion) {
      this.registrosSeleccionados = orden.registros_produccion;
    }
  }

  /**
   * RF-12, RF-13, RF-14: Registrar producción
   */
  registrarProduccion(): void {
    if (!this.ordenSeleccionada) {
      this.snackBar.open('Por favor selecciona una orden', 'Cerrar', { duration: 3000 });
      return;
    }

    if (this.formRegistroProduccion.invalid) {
      this.snackBar.open('Por favor completa los campos requeridos', 'Cerrar', { duration: 3000 });
      return;
    }

    const datos = {
      ...this.formRegistroProduccion.value,
      orden_produccion_id: this.ordenSeleccionada.id
    };

    this.produccionService.crearRegistro(datos).subscribe({
      next: (registro) => {
        this.registrosSeleccionados.push(registro);
        
        // Actualizar orden
        if (this.ordenSeleccionada) {
          this.produccionService.obtenerOrden(this.ordenSeleccionada.id).subscribe({
            next: (ordenActualizada) => {
              this.ordenSeleccionada = ordenActualizada;
            }
          });
        }

        this.formRegistroProduccion.reset();
        this.snackBar.open('Registro de producción creado exitosamente', 'Cerrar', { duration: 3000 });
      },
      error: (error) => {
        console.error('Error registrando producción:', error);
        this.snackBar.open('Error al registrar producción', 'Cerrar', { duration: 3000 });
      }
    });
  }

  /**
   * Completar una orden de producción
   */
  completarOrden(orden: OrdenProduccion): void {
    if (confirm(`¿Deseas marcar la orden ${orden.numero_orden} como completada?`)) {
      this.produccionService.completarOrden(orden.id).subscribe({
        next: (ordenActualizada) => {
          const index = this.ordenesProduccion.findIndex(o => o.id === orden.id);
          if (index !== -1) {
            this.ordenesProduccion[index] = ordenActualizada;
          }
          this.snackBar.open('Orden completada exitosamente', 'Cerrar', { duration: 3000 });
        },
        error: (error) => {
          console.error('Error completando orden:', error);
          this.snackBar.open('Error al completar orden', 'Cerrar', { duration: 3000 });
        }
      });
    }
  }

  /**
   * Obtener nombre del lote asociado
   */
  getNombreLote(loteId: number): string {
    const lote = this.lotesDisponibles.find(l => l.id === loteId);
    return lote ? lote.numero_lote : `Lote #${loteId}`;
  }

  /**
   * Obtener referencia del lote
   */
  getReferencia(loteId: number): string {
    const lote = this.lotesDisponibles.find(l => l.id === loteId);
    return lote ? lote.referencia_nombre : '-';
  }

  /**
   * Obtener cantidad de registros
   */
  getCantidadRegistros(orden: OrdenProduccion): number {
    return orden.registros_produccion ? orden.registros_produccion.length : 0;
  }

  /**
   * Calcular total producido
   */
  getTotalProducido(registros?: RegistroProduccion[]): number {
    if (!registros) return 0;
    return registros.reduce((suma, r) => suma + r.cantidad_producida, 0);
  }

  /**
   * Calcular total rechazado
   */
  getTotalRechazado(registros?: RegistroProduccion[]): number {
    if (!registros) return 0;
    return registros.reduce((suma, r) => suma + r.cantidad_rechazada, 0);
  }

  /**
   * Calcular tiempo total
   */
  getTiempoTotal(registros?: RegistroProduccion[]): string {
    if (!registros) return '0h';
    const totalMinutos = registros.reduce((suma, r) => suma + (r.tiempo_total_minutos || 0), 0);
    const horas = Math.floor(totalMinutos / 60);
    const minutos = totalMinutos % 60;
    return `${horas}h ${minutos}m`;
  }

  getOperacionLabel(operacion: TipoOperacion | string): string {
    return this.operacionesLabels[operacion as TipoOperacion];
  }

  // Labels para estados
  getEstadoLabel(estado: EstadoOrdenProduccion | string): string {
    return this.estadoOrdenLabels[estado as EstadoOrdenProduccion];
  }
}

