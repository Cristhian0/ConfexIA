import { Component, OnInit, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatTable } from '@angular/material/table';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTabChangeEvent } from '@angular/material/tabs';
import { forkJoin } from 'rxjs';
import { ColillaService } from '../../services/colilla.service';
import { LoteService } from '../../services/lote.service';
import { TallerService } from '../../services/taller.service';
import { ColillaListItem, EstadoColilla, TipoTrabajo, ColillasPorConfeccionista } from '../../models/colilla.model';
import { Lote } from '../../models/lote.model';
import { Taller } from '../../models/taller.model';
import { FirmaDialogComponent } from './firma-dialog.component';

@Component({
  selector: 'app-colillas',
  templateUrl: './colillas.component.html',
  styleUrls: ['./colillas.component.scss']
})
export class ColillasComponent implements OnInit {
  // Datos principales
  colillas: ColillaListItem[] = [];
  colillasPorConfeccionista: ColillasPorConfeccionista = {};
  talleres: Taller[] = [];
  lotes: Lote[] = [];

  // Formularios
  formNuevaColilla: FormGroup;
  formCargaPDF: FormGroup;
  formFiltros: FormGroup;

  // Control de estado
  loading = false;
  tabActual = 0;
  tallerId: number | null = null;
  loteId: number | null = null;

  // UI - Tabla de colillas
  @ViewChild(MatTable, { static: false }) tabla!: MatTable<ColillaListItem>;
  @ViewChild(MatPaginator, { static: false }) paginator!: MatPaginator;
  @ViewChild(MatSort, { static: false }) sort!: MatSort;

  displayedColumns: string[] = [
    'numero_colilla',
    'confeccionista_nombre',
    'tipo_trabajo',
    'cantidad_prendas',
    'cantidad_completada',
    'estado',
    'fecha_limite_entrega',
    'acciones'
  ];

  displayedColumnsPorConf: string[] = [
    'confeccionista',
    'total_colillas',
    'total_prendas',
    'total_completadas',
    'total_rechazadas',
    'acciones'
  ];

  // Enums para template
  EstadoColilla = EstadoColilla;
  TipoTrabajo = TipoTrabajo;

  objectKeys = Object.keys;

  estadoLabels: { [key: string]: string } = {
    [EstadoColilla.PENDIENTE]: 'Pendiente',
    [EstadoColilla.EN_PROCESO]: 'En Proceso',
    [EstadoColilla.COMPLETADA]: 'Completada',
    [EstadoColilla.CANCELADA]: 'Cancelada'
  };

  tipoTrabajoLabels: { [key: string]: string } = {
    [TipoTrabajo.ENSAMBLE]: 'Ensamble',
    [TipoTrabajo.COSTURA]: 'Costura',
    [TipoTrabajo.FILETEADO]: 'Fileteado',
    [TipoTrabajo.TERMINACION]: 'Terminación',
    [TipoTrabajo.OTRO]: 'Otro'
  };

  constructor(
    private colillaService: ColillaService,
    private loteService: LoteService,
    private tallerService: TallerService,
    private fb: FormBuilder,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {
    this.formNuevaColilla = this.crearFormularioColilla();
    this.formCargaPDF = this.crearFormularioPDF();
    this.formFiltros = this.crearFormularioFiltros();
  }

  ngOnInit(): void {
    this.cargarDatos();
  }

  cargarDatos(): void {
    this.loading = true;
    forkJoin([
      this.tallerService.listar(true),
      this.loteService.listar() // Carga todos los lotes disponibles
    ]).subscribe(
      ([talleres, lotes]) => {
        this.talleres = talleres || [];
        this.lotes = lotes || [];
        console.log(`Cargados ${this.lotes.length} lotes y ${this.talleres.length} talleres`);
        this.cargarColillas();
      },
      (error) => {
        console.error('Error cargando datos:', error);
        this.snackBar.open('Error al cargar datos', 'Cerrar', { duration: 5000 });
        this.loading = false;
      }
    );
  }

  cargarColillas(): void {
    const tallerId = this.formFiltros.get('taller_id')?.value;
    const loteId = this.formFiltros.get('lote_id')?.value;

    this.colillaService.listarColillas(0, 1000, tallerId, loteId).subscribe(
      (data) => {
        this.colillas = data;
        this.loading = false;
        if (tallerId) {
          this.cargarColillasPorConfeccionista(tallerId);
        }
      },
      (error) => {
        console.error('Error cargando colillas:', error);
        this.snackBar.open('Error al cargar colillas', 'Cerrar', { duration: 5000 });
        this.loading = false;
      }
    );
  }

  cargarColillasPorConfeccionista(tallerId: number): void {
    this.colillaService.colillasPorConfeccionista(tallerId).subscribe(
      (data) => {
        this.colillasPorConfeccionista = data;
      },
      (error) => {
        console.error('Error cargando colillas por confeccionista:', error);
      }
    );
  }

  refrescarLotes(): void {
    this.loading = true;
    this.loteService.listar().subscribe(
      (lotes) => {
        this.lotes = lotes || [];
        console.log(`Refrescados ${this.lotes.length} lotes`);
        this.snackBar.open(`${this.lotes.length} lotes disponibles`, 'Cerrar', { duration: 3000 });
        this.loading = false;
      },
      (error) => {
        console.error('Error refrescando lotes:', error);
        this.snackBar.open('Error al refrescar lotes', 'Cerrar', { duration: 5000 });
        this.loading = false;
      }
    );
  }

  crearFormularioColilla(): FormGroup {
    return this.fb.group({
      lote_id: ['', [Validators.required]],
      taller_id: ['', [Validators.required]],
      confeccionista_nombre: ['', [Validators.required, Validators.maxLength(200)]],
      confeccionista_cedula: ['', [Validators.maxLength(20)]],
      tipo_trabajo: ['', [Validators.required]],
      cantidad_prendas: ['', [Validators.required, Validators.min(1)]],
      descripcion_trabajo: [''],
      referencia: [''],
      talla_id: [''],
      color: [''],
      fecha_limite_entrega: [''],
      observaciones: ['']
    });
  }

  crearFormularioPDF(): FormGroup {
    return this.fb.group({
      archivo: ['', [Validators.required]]
    });
  }

  crearFormularioFiltros(): FormGroup {
    return this.fb.group({
      taller_id: [''],
      lote_id: [''],
      estado: ['']
    });
  }

  onLoteSeleccionado(loteId: number): void {
    if (!loteId) return;

    const loteSeleccionado = this.lotes.find(l => l.id === loteId);
    if (loteSeleccionado) {
      // Auto-completar campos relacionados con el lote
      const patchData: any = {};

      if (loteSeleccionado.referencia_nombre && !this.formNuevaColilla.get('referencia')?.value) {
        patchData.referencia = loteSeleccionado.referencia_nombre;
      }

      // Si hay detalles del lote con colores, usar el primer color disponible
      if (loteSeleccionado.detalles && loteSeleccionado.detalles.length > 0) {
        const primerDetalle = loteSeleccionado.detalles[0];
        if (primerDetalle.color_nombre && !this.formNuevaColilla.get('color')?.value) {
          patchData.color = primerDetalle.color_nombre;
        }
      }

      if (Object.keys(patchData).length > 0) {
        this.formNuevaColilla.patchValue(patchData);
        const camposAutocompletados = Object.keys(patchData).join(', ');
        this.snackBar.open(`Campos autocompletados: ${camposAutocompletados}`, 'Cerrar', { duration: 3000 });
      }
    }
  }

  // ========== CREAR COLILLA ==========
  crearColilla(): void {
    if (this.formNuevaColilla.invalid) {
      this.snackBar.open('Por favor completa todos los campos requeridos', 'Cerrar', { duration: 5000 });
      return;
    }

    const dialogRef = this.dialog.open(FirmaDialogComponent, {
      width: '680px',
      disableClose: true
    });

    dialogRef.afterClosed().subscribe((firmaBase64: string | undefined) => {
      if (!firmaBase64) {
        this.snackBar.open('Firma cancelada. No se creó la colilla.', 'Cerrar', { duration: 5000 });
        return;
      }

      this.guardarColillaConFirma(firmaBase64);
    });
  }

  private guardarColillaConFirma(firmaBase64: string): void {
    this.loading = true;
    const rawData = this.formNuevaColilla.value;
    const colillaData = {
      ...rawData,
      lote_id: rawData.lote_id ? Number(rawData.lote_id) : undefined,
      taller_id: rawData.taller_id ? Number(rawData.taller_id) : undefined,
      cantidad_prendas: rawData.cantidad_prendas ? Number(rawData.cantidad_prendas) : undefined,
      talla_id: rawData.talla_id ? Number(rawData.talla_id) : undefined,
      firma_base64: firmaBase64
    };

    // Limpiar campos vacíos y convertir a null
    Object.keys(colillaData).forEach(key => {
      if (colillaData[key] === '' || colillaData[key] === null) {
        colillaData[key] = null;
      }
    });

    // Convertir strings numéricos a números
    if (colillaData.lote_id) colillaData.lote_id = Number(colillaData.lote_id);
    if (colillaData.taller_id) colillaData.taller_id = Number(colillaData.taller_id);
    if (colillaData.talla_id) colillaData.talla_id = Number(colillaData.talla_id);
    if (colillaData.cantidad_prendas) colillaData.cantidad_prendas = Number(colillaData.cantidad_prendas);

    this.colillaService.crearColilla(colillaData).subscribe(
      (colilla) => {
        this.snackBar.open(`Colilla ${colilla.numero_colilla} creada exitosamente`, 'Cerrar', { duration: 5000 });
        this.formNuevaColilla.reset();
        this.cargarColillas();
        this.loading = false;
      },
      (error) => {
        console.error('Error creando colilla:', error);
        this.snackBar.open('Error al crear colilla', 'Cerrar', { duration: 5000 });
        this.loading = false;
      }
    );
  }

  descargarPdfColillaFirmada(colillaId: number, firmaBase64: string): void {
    this.loading = true;
    this.colillaService.descargarPdfColillaFirmada(colillaId, firmaBase64).subscribe(
      (blob) => {
        this.colillaService.abrirPdf(blob, `Colilla_${colillaId}.pdf`);
        this.loading = false;
        this.snackBar.open('PDF firmado descargado', 'Cerrar', { duration: 3000 });
      },
      (error) => {
        console.error('Error descargando PDF firmado:', error);
        this.snackBar.open('Error al descargar PDF firmado', 'Cerrar', { duration: 5000 });
        this.loading = false;
      }
    );
  }

  // ========== ACTUALIZAR ESTADO ==========
  abrirDialogoActualizarEstado(colilla: ColillaListItem): void {
    // Para simplificar, usaremos un prompt o diálogo simple
    const nuevoEstado = confirm(
      `Cambiar estado de colilla ${colilla.numero_colilla} a:\n- OK para Completada\n- CANCELAR para cancelar`
    ) ? EstadoColilla.COMPLETADA : null;

    if (nuevoEstado) {
      this.actualizarEstado(colilla.id, nuevoEstado);
    }
  }

  actualizarEstado(colillaId: number, estado: EstadoColilla): void {
    this.loading = true;
    this.colillaService.actualizarEstado(colillaId, estado).subscribe(
      (colilla) => {
        this.snackBar.open(`Estado actualizado: ${estado}`, 'Cerrar', { duration: 5000 });
        this.cargarColillas();
      },
      (error) => {
        console.error('Error actualizando estado:', error);
        this.snackBar.open('Error al actualizar estado', 'Cerrar', { duration: 5000 });
        this.loading = false;
      }
    );
  }

  // ========== DESCARGA DE PDFS ==========
  descargarPdfColilla(colillaId: number, numeroColilla: string): void {
    this.loading = true;
    this.colillaService.descargarPdfColilla(colillaId).subscribe(
      (blob) => {
        this.colillaService.abrirPdf(blob, `Colilla_${numeroColilla}.pdf`);
        this.loading = false;
        this.snackBar.open('PDF descargado', 'Cerrar', { duration: 3000 });
      },
      (error) => {
        console.error('Error descargando PDF:', error);
        this.snackBar.open('Error al descargar PDF', 'Cerrar', { duration: 5000 });
        this.loading = false;
      }
    );
  }

  descargarPdfTaller(tallerId: number): void {
    if (!tallerId) {
      this.snackBar.open('Por favor selecciona un taller', 'Cerrar', { duration: 3000 });
      return;
    }

    this.loading = true;
    this.colillaService.descargarPdfTaller(tallerId).subscribe(
      (blob) => {
        this.colillaService.abrirPdf(blob, `Colillas_Taller_${tallerId}.pdf`);
        this.loading = false;
        this.snackBar.open('PDF descargado', 'Cerrar', { duration: 3000 });
      },
      (error) => {
        console.error('Error descargando PDF:', error);
        this.snackBar.open('Error al descargar PDF', 'Cerrar', { duration: 5000 });
        this.loading = false;
      }
    );
  }

  descargarPdfLote(loteId: number): void {
    if (!loteId) {
      this.snackBar.open('Por favor selecciona un lote', 'Cerrar', { duration: 3000 });
      return;
    }

    this.loading = true;
    this.colillaService.descargarPdfLote(loteId).subscribe(
      (blob) => {
        this.colillaService.abrirPdf(blob, `Colillas_Lote_${loteId}.pdf`);
        this.loading = false;
        this.snackBar.open('PDF descargado', 'Cerrar', { duration: 3000 });
      },
      (error) => {
        console.error('Error descargando PDF:', error);
        this.snackBar.open('Error al descargar PDF', 'Cerrar', { duration: 5000 });
        this.loading = false;
      }
    );
  }

  visualizarPdfColilla(colillaId: number): void {
    this.loading = true;
    this.colillaService.descargarPdfColilla(colillaId).subscribe(
      (blob) => {
        this.colillaService.visualizarPdf(blob);
        this.loading = false;
      },
      (error) => {
        console.error('Error visualizando PDF:', error);
        this.snackBar.open('Error al visualizar PDF', 'Cerrar', { duration: 5000 });
        this.loading = false;
      }
    );
  }

  // ========== CARGA DE PDF ==========
  onArchivoSeleccionado(event: any): void {
    const archivo = event.target.files[0];
    if (archivo) {
      this.formCargaPDF.patchValue({ archivo: archivo.name });
      this.snackBar.open(`Archivo seleccionado: ${archivo.name}`, 'Cerrar', { duration: 3000 });
      // TODO: Procesar el PDF cargado (parsear y extraer datos)
    }
  }

  cargarPDF(): void {
    // Esta funcionalidad estaría disponible después
    this.snackBar.open('Carga de PDF en desarrollo', 'Cerrar', { duration: 3000 });
  }

  // ========== FILTROS ==========
  aplicarFiltros(): void {
    this.cargarColillas();
  }

  limpiarFiltros(): void {
    this.formFiltros.reset();
    this.cargarColillas();
  }

  // ========== EVENTOS DE TAB ==========
  onTabChange(event: MatTabChangeEvent): void {
    this.tabActual = event.index;
    if (event.index === 1) {
      const tallerId = this.formFiltros.get('taller_id')?.value;
      if (tallerId) {
        this.cargarColillasPorConfeccionista(tallerId);
      }
    }
  }

  // ========== UTILIDADES ==========
  obtenerNombreTaller(tallerId: number): string {
    const taller = this.talleres.find(t => t.id === tallerId);
    return taller ? taller.nombre : 'Desconocido';
  }

  obtenerNombreLote(loteId: number): string {
    const lote = this.lotes.find(l => l.id === loteId);
    return lote ? `Lote ${lote.numero_lote}` : 'Desconocido';
  }

  eliminarColilla(colillaId: number): void {
    if (confirm('¿Estás seguro de que deseas eliminar esta colilla?')) {
      this.loading = true;
      this.colillaService.eliminarColilla(colillaId).subscribe(
        () => {
          this.snackBar.open('Colilla eliminada', 'Cerrar', { duration: 3000 });
          this.cargarColillas();
        },
        (error) => {
          console.error('Error eliminando colilla:', error);
          this.snackBar.open('Error al eliminar colilla', 'Cerrar', { duration: 5000 });
          this.loading = false;
        }
      );
    }
  }
}
