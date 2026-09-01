import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { CalidadService } from '../../services/calidad.service';
import { ProduccionService } from '../../services/produccion.service';
import {
  InspeccionCalidad,
  InspeccionCalidadCreate,
  InspeccionCalidadUpdate,
  TipoDefecto,
  ClasificacionInspeccion,
  DefectoInspeccionCreate,
  DefectoInspeccion
} from '../../models/produccion.model';
import { OrdenProduccion } from '../../models';

@Component({
  selector: 'app-calidad',
  templateUrl: './calidad.component.html',
  styleUrls: ['./calidad.component.scss']
})
export class CalidadComponent implements OnInit {
  // Propiedades generales
  inspecciones: InspeccionCalidad[] = [];
  ordenesProduccion: OrdenProduccion[] = [];
  
  // Tipos y clasificaciones
  tiposDefecto = Object.values(TipoDefecto);
  clasificaciones = Object.values(ClasificacionInspeccion);
  estadosPago = ['Pagado', 'Pendiente', 'Atrasado'];
  
  // Controles de vista
  mostrarFormulario = false;
  mostrarFormularioDefecto = false;
  selectedInspeccion: InspeccionCalidad | null = null;
  selectedDefectos: DefectoInspeccion[] = [];
  
  // Filtros
  filtroOrdenId: number | null = null;
  filtroClasificacion: string = '';
  filtroInspector: string = '';
  
  // Formularios
  formularioInspeccion!: FormGroup;
  formularioDefecto!: FormGroup;
  formularioCalidad!: FormGroup;
  
  // Control de UI
  cargando = false;
  errorMensaje = '';
  exitoMensaje = '';
  porcentajes: any = null;
  puedeReingresar = false;

  constructor(
    private calidad: CalidadService,
    private produccionService: ProduccionService,
    private fb: FormBuilder
  ) {
    this.inicializarFormularios();
  }

  ngOnInit(): void {
    this.cargarInspecciones();
    this.cargarOrdenes();
  }

  // ========== Inicialización ==========
  
  inicializarFormularios(): void {
    this.formularioInspeccion = this.fb.group({
      orden_produccion_id: ['', Validators.required],
      inspector: ['', [Validators.required, Validators.minLength(3)]],
      clasificacion: [ClasificacionInspeccion.OK, Validators.required],
      cantidad_inspeccionada: ['', [Validators.required, Validators.min(1)]],
      cantidad_ok: [0, [Validators.required, Validators.min(0)]],
      cantidad_reproceso: [0, [Validators.required, Validators.min(0)]],
      cantidad_defectuosa: [0, [Validators.required, Validators.min(0)]],
      observaciones: [''],
      reingresar_produccion: [false]
    });

    this.formularioDefecto = this.fb.group({
      tipo_defecto: [TipoDefecto.COSTURA, Validators.required],
      cantidad_defectos: [1, [Validators.required, Validators.min(1)]],
      descripcion: [''],
      recomendacion: ['']
    });

    this.formularioCalidad = this.fb.group({
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

  // ========== Carga de datos ==========
  
  cargarInspecciones(): void {
    this.cargando = true;
    this.calidad.listarInspecciones(
      this.filtroOrdenId || undefined,
      this.filtroClasificacion || undefined,
      this.filtroInspector || undefined
    ).subscribe({
      next: (data) => {
        this.inspecciones = data;
        this.cargando = false;
      },
      error: (error) => {
        this.errorMensaje = 'Error al cargar inspecciones: ' + error.message;
        this.cargando = false;
      }
    });
  }

  cargarOrdenes(): void {
    this.produccionService.listarOrdenes().subscribe({
      next: (data) => {
        this.ordenesProduccion = data;
      },
      error: (error) => {
        console.error('Error al cargar órdenes:', error);
      }
    });
  }

  // ========== RF-15: Crear inspección ==========
  
  crearInspeccion(): void {
    if (this.formularioInspeccion.invalid) {
      this.errorMensaje = 'Por favor completa todos los campos requeridos';
      return;
    }

    // Validar que las cantidades sumen la cantidad inspeccionada
    const datos = this.formularioInspeccion.value;
    const sumaOk = (datos.cantidad_ok || 0) + (datos.cantidad_reproceso || 0) + (datos.cantidad_defectuosa || 0);
    
    if (sumaOk !== parseInt(datos.cantidad_inspeccionada)) {
      this.errorMensaje = `La suma de cantidades (${sumaOk}) debe igualar la cantidad inspeccionada (${datos.cantidad_inspeccionada})`;
      return;
    }

    this.cargando = true;
    const inspeccion: InspeccionCalidadCreate = datos;
    
    this.calidad.crearInspeccion(inspeccion).subscribe({
      next: (data) => {
        this.exitoMensaje = `Inspección ${data.numero_inspeccion} creada exitosamente`;
        this.formularioInspeccion.reset({ clasificacion: ClasificacionInspeccion.OK, reingresar_produccion: false });
        this.mostrarFormulario = false;
        this.cargarInspecciones();
        this.cargando = false;
        setTimeout(() => this.exitoMensaje = '', 3000);
      },
      error: (error) => {
        this.errorMensaje = 'Error al crear inspección: ' + error.message;
        this.cargando = false;
      }
    });
  }

  // ========== RF-16: Actualizar clasificación ==========
  
  actualizarClasificacion(nuevaClasificacion: ClasificacionInspeccion): void {
    if (!this.selectedInspeccion) return;

    const actualizacion: InspeccionCalidadUpdate = {
      clasificacion: nuevaClasificacion
    };

    this.cargando = true;
    this.calidad.actualizarInspeccion(this.selectedInspeccion.id, actualizacion).subscribe({
      next: (data) => {
        this.selectedInspeccion = data;
        this.exitoMensaje = 'Clasificación actualizada exitosamente';
        this.cargarInspecciones();
        this.cargando = false;
        setTimeout(() => this.exitoMensaje = '', 3000);
      },
      error: (error) => {
        this.errorMensaje = 'Error al actualizar clasificación: ' + error.message;
        this.cargando = false;
      }
    });
  }

  // ========== RF-17: Agregar defecto ==========
  
  agregarDefecto(): void {
    if (!this.selectedInspeccion || this.formularioDefecto.invalid) {
      this.errorMensaje = 'Por favor completa todos los campos del defecto';
      return;
    }

    const defecto: DefectoInspeccionCreate = this.formularioDefecto.value;
    
    this.cargando = true;
    this.calidad.agregarDefecto(this.selectedInspeccion.id, defecto).subscribe({
      next: () => {
        this.exitoMensaje = 'Defecto agregado exitosamente';
        this.formularioDefecto.reset({ tipo_defecto: TipoDefecto.COSTURA, cantidad_defectos: 1 });
        this.mostrarFormularioDefecto = false;
        this.cargarDetalle(this.selectedInspeccion!.id);
        this.cargando = false;
        setTimeout(() => this.exitoMensaje = '', 3000);
      },
      error: (error) => {
        this.errorMensaje = 'Error al agregar defecto: ' + error.message;
        this.cargando = false;
      }
    });
  }

  eliminarDefecto(defectoId: number): void {
    if (!confirm('¿Estás seguro de que quieres eliminar este defecto?')) return;

    this.cargando = true;
    this.calidad.eliminarDefecto(defectoId).subscribe({
      next: () => {
        this.exitoMensaje = 'Defecto eliminado exitosamente';
        if (this.selectedInspeccion) {
          this.cargarDetalle(this.selectedInspeccion.id);
        }
        this.cargando = false;
        setTimeout(() => this.exitoMensaje = '', 3000);
      },
      error: (error) => {
        this.errorMensaje = 'Error al eliminar defecto: ' + error.message;
        this.cargando = false;
      }
    });
  }

  // ========== RF-18: Reingresar a producción ==========
  
  verificarPuedeReingresar(): void {
    if (!this.selectedInspeccion) return;

    this.calidad.verificarPuedeReingresar(this.selectedInspeccion.id).subscribe({
      next: (respuesta) => {
        this.puedeReingresar = respuesta.puede_reingresar;
      },
      error: (error) => {
        this.puedeReingresar = false;
        console.error('Error verificando elegibilidad:', error);
      }
    });
  }

  marcarReingresar(): void {
    if (!this.selectedInspeccion) return;

    if (!confirm('¿Estás seguro de que quieres marcar esta inspección para reingresar a producción?')) return;

    this.cargando = true;
    this.calidad.marcarReingresar(this.selectedInspeccion.id).subscribe({
      next: (data) => {
        this.selectedInspeccion = data;
        this.exitoMensaje = 'Prenda marcada para reingresar a producción';
        this.cargarInspecciones();
        this.cargando = false;
        setTimeout(() => this.exitoMensaje = '', 3000);
      },
      error: (error) => {
        this.errorMensaje = 'Error al marcar para reingresar: ' + error.message;
        this.cargando = false;
      }
    });
  }

  // ========== Navegación y detalles ==========
  
  cargarDetalle(inspeccionId: number): void {
    this.cargando = true;
    this.calidad.obtenerInspeccion(inspeccionId).subscribe({
      next: (data) => {
        this.selectedInspeccion = data;
        this.selectedDefectos = data.defectos || [];
        this.formularioCalidad.patchValue({
          fecha_recepcion: '',
          revisado_por: '',
          cantidad_parcial: 0,
          cantidad_arreglos: 0,
          cantidad_imperfecciones: 0,
          cantidad_pendiente: 0,
          requiere_compras: false,
          fecha_entrega_total: '',
          dias_mora: 0,
          estado_pago: ''
        });
        this.obtenerResumen(inspeccionId);
        this.verificarPuedeReingresar();
        this.cargando = false;
      },
      error: (error) => {
        this.errorMensaje = 'Error al cargar detalles: ' + error.message;
        this.cargando = false;
      }
    });
  }

  obtenerResumen(inspeccionId: number): void {
    this.calidad.obtenerResumenInspeccion(inspeccionId).subscribe({
      next: (data) => {
        this.porcentajes = data;
      },
      error: (error) => {
        console.error('Error al obtener resumen:', error);
      }
    });
  }

  volver(): void {
    this.selectedInspeccion = null;
    this.mostrarFormulario = false;
    this.mostrarFormularioDefecto = false;
    this.porcentajes = null;
  }

  // ========== Filtros ==========
  
  aplicarFiltros(): void {
    this.cargarInspecciones();
  }

  limpiarFiltros(): void {
    this.filtroOrdenId = null;
    this.filtroClasificacion = '';
    this.filtroInspector = '';
    this.cargarInspecciones();
  }

  // ========== Utilidades ==========
  
  getClasificacionClase(clasificacion: ClasificacionInspeccion): string {
    switch (clasificacion) {
      case ClasificacionInspeccion.OK:
        return 'clasificacion-ok';
      case ClasificacionInspeccion.REPROCESO:
        return 'clasificacion-reproceso';
      case ClasificacionInspeccion.DEFECTUOSA:
        return 'clasificacion-defectuosa';
      default:
        return '';
    }
  }

  getTipoDefectoLabel(tipo: TipoDefecto): string {
    const labels: { [key in TipoDefecto]: string } = {
      [TipoDefecto.COSTURA]: 'Costura',
      [TipoDefecto.MEDIDA]: 'Medida',
      [TipoDefecto.MANCHA]: 'Mancha',
      [TipoDefecto.TELA]: 'Tela'
    };
    return labels[tipo] || tipo;
  }

  getClasificacionLabel(clasificacion: ClasificacionInspeccion): string {
    const labels: { [key in ClasificacionInspeccion]: string } = {
      [ClasificacionInspeccion.OK]: 'OK',
      [ClasificacionInspeccion.REPROCESO]: 'Reproceso',
      [ClasificacionInspeccion.DEFECTUOSA]: 'Defectuosa'
    };
    return labels[clasificacion] || clasificacion;
  }
}
