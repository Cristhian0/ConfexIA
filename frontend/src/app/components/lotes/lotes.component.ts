import { Component, OnInit, ChangeDetectorRef, ViewEncapsulation } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { LoteService } from '../../services/lote.service';
import { CatalogoService } from '../../services/catalogo.service';
import { TallerService } from '../../services/taller.service';
import { CorteService } from '../../services/corte.service';
import { Lote, EstadoLote } from '../../models/lote.model';
import { LoteFormComponent } from './lote-form/lote-form.component';
import { ImportacionExcelComponent } from './importacion-excel/importacion-excel.component';
import { TrazabilidadComponent } from '../trazabilidad/trazabilidad.component';
import { Referencia } from '../../models/referencia.model';
import { Material } from '../../models/material.model';
import { Color } from '../../models/color.model';
import { OrdenCorteBasica } from '../../models/lote.model';

@Component({
  selector: 'app-lotes',
  templateUrl: './lotes.component.html',
  styleUrls: ['./lotes.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class LotesComponent implements OnInit {
  lotes: Lote[] = [];
  referencias: Referencia[] = [];
  materiales: Material[] = [];
  colores: Color[] = [];
  tallas: any[] = [];
  remisionesPorLote: { [key: number]: any[] } = {};
  ordenesCorte: OrdenCorteBasica[] = [];
  displayedColumns: string[] = ['mesa','fecha_corte','referencia','colores','material_total','tallas','fecha_entrega','fecha_estimada','despacha','confeccionista','remision','cantidad_total','acciones'];
  loading = false;

  constructor(
    private loteService: LoteService,
    private catalogoService: CatalogoService,
    private tallerService: TallerService,
    private corteService: CorteService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
    private cdr: ChangeDetectorRef
  ) { }

  ngOnInit(): void {
    // Cargar catálogos y lotes en paralelo
    this.cargarCatalogos();
    this.cargarOrdenesCorte();
    this.cargarLotes();
    this.cargarRemisiones();
  }

  cargarCatalogos(): void {
    // Cargar referencias
    this.catalogoService.listarReferencias(true).subscribe({
      next: (data) => {
        this.referencias = data || [];
        console.log(`Referencias cargadas: ${this.referencias.length}`);
        this.cdr.detectChanges();
      },
      error: (error) => {
        console.error('Error cargando referencias:', error);
        this.referencias = [];
      }
    });
    
    // Cargar materiales
    this.catalogoService.listarMateriales(true).subscribe({
      next: (data) => {
        this.materiales = data || [];
        console.log(`Materiales cargados: ${this.materiales.length}`);
        this.cdr.detectChanges();
      },
      error: (error) => {
        console.error('Error cargando materiales:', error);
        this.materiales = [];
      }
    });
    
    // Cargar colores
    this.catalogoService.listarColores(true).subscribe({
      next: (data) => {
        this.colores = data || [];
        console.log(`Colores cargados: ${this.colores.length}`);
      },
      error: (error) => {
        console.error('Error cargando colores:', error);
        this.colores = [];
      }
    });

    // Cargar tallas
    this.catalogoService.listarTallas(true).subscribe({
      next: (data) => {
        this.tallas = data || [];
      },
      error: (error) => {
        console.error('Error cargando tallas:', error);
        this.tallas = [];
      }
    });
  }

  cargarLotes(): void {
    this.loading = true;
    this.loteService.listar().subscribe({
      next: (data) => {
        this.lotes = data || [];
        this.loading = false;
        this.cdr.detectChanges();
        // Si los catálogos aún no están cargados, intentar recargarlos
        if ((!this.referencias || this.referencias.length === 0) || 
            (!this.materiales || this.materiales.length === 0)) {
          this.cargarCatalogos();
        }
      },
      error: (error) => {
        console.error('Error cargando lotes:', error);
        this.snackBar.open('Error al cargar lotes', 'Cerrar', { duration: 3000 });
        this.loading = false;
      }
    });
  }

  abrirFormulario(lote?: Lote): void {
    const dialogRef = this.dialog.open(LoteFormComponent, {
      width: '800px',
      data: lote
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.cargarLotes();
      }
    });
  }

  eliminarLote(id: number): void {
    if (confirm('¿Está seguro de eliminar este lote?')) {
      this.loteService.eliminar(id).subscribe({
        next: () => {
          this.snackBar.open('Lote eliminado correctamente', 'Cerrar', { duration: 3000 });
          this.cargarLotes();
        },
        error: (error) => {
          console.error('Error eliminando lote:', error);
          this.snackBar.open('Error al eliminar lote', 'Cerrar', { duration: 3000 });
        }
      });
    }
  }

  getEstadoLabel(estado: EstadoLote): string {
    const estados: { [key: string]: string } = {
      'en_corte': 'En Corte',
      'corte_completado': 'Corte Completado',
      'en_camino': 'En Camino',
      'en_taller': 'En Taller',
      'en_confeccion': 'En Confección',
      'parcialmente_entregado': 'Parcialmente Entregado',
      'completado': 'Completado',
      'cancelado': 'Cancelado'
    };
    return estados[estado] || estado;
  }

  cargarOrdenesCorte(): void {
    this.corteService.listarOrdenes().subscribe({
      next: (data) => {
        this.ordenesCorte = data.map(orden => ({
          id: orden.id,
          numero_orden: orden.numero_orden,
          tipo_prenda: orden.tipo_prenda,
          estado: orden.estado,
          fecha_creacion: orden.created_at
        }));
        console.log(`Órdenes de corte cargadas: ${this.ordenesCorte.length}`);
      },
      error: (error) => {
        console.error('Error cargando órdenes de corte:', error);
        this.ordenesCorte = [];
      }
    });
  }

  cargarRemisiones(): void {
    // Cargar todas las remisiones y agrupar por lote
    this.tallerService.listarRemisiones().subscribe({
      next: (data) => {
        this.remisionesPorLote = {};
        (data || []).forEach(r => {
          if (!this.remisionesPorLote[r.lote_id]) this.remisionesPorLote[r.lote_id] = [];
          this.remisionesPorLote[r.lote_id].push(r);
        });
      },
      error: (error) => {
        console.error('Error cargando remisiones:', error);
        this.remisionesPorLote = {};
      }
    });
  }

  getOrdenCorteInfo(lote: Lote): string {
    if (!lote.orden_corte_id) {
      return '-';
    }
    const orden = this.ordenesCorte.find(o => o.id === lote.orden_corte_id);
    return orden ? `${orden.numero_orden} (${orden.estado})` : `ID: ${lote.orden_corte_id}`;
  }

  verTrazabilidad(lote: Lote): void {
    const dialogRef = this.dialog.open(TrazabilidadComponent, {
      width: '90vw',
      maxWidth: '1200px',
      data: { loteId: lote.id, ordenCorteId: lote.orden_corte_id }
    });
  }

  abrirImportacion(): void {
    const dialogRef = this.dialog.open(ImportacionExcelComponent, {
      width: '600px'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.cargarLotes();
      }
    });
  }

  getReferenciaNombre(lote: Lote): string {
    // El nombre siempre viene del backend
    return lote.referencia_nombre || '-';
  }

  getMaterialNombre(lote: Lote): string {
    // El nombre siempre viene del backend
    return lote.material_nombre || '-';
  }

  getColoresLote(lote: Lote): string {
    if (!lote.detalles || lote.detalles.length === 0) {
      return 'Sin colores';
    }
    const coloresUnicos = new Set<string>();
    lote.detalles.forEach(d => {
      if (d.color_nombre && d.color_nombre.trim()) {
        coloresUnicos.add(d.color_nombre);
      }
    });
    return Array.from(coloresUnicos).join(', ') || 'Sin colores';
  }

  tallaNombre(id: number): string {
    const t = this.tallas.find(tt => tt.id === id);
    return t ? (t.codigo || t.nombre || (`ID:${id}`)) : `ID:${id}`;
  }

  getTallasLote(lote: Lote): string {
    if (!lote.detalles || lote.detalles.length === 0) return '-';
    return lote.detalles.map(d => `${this.tallaNombre(d.talla_id)}:${d.cantidad}`).join('; ');
  }

  getRemisionesInfo(lote: Lote): any[] {
    return this.remisionesPorLote[lote.id] || [];
  }

  getRemisionesString(lote: Lote): string {
    // Preferir el número de remisión guardado directamente en el lote
    if ((lote as any).remision_numero) return (lote as any).remision_numero;
    const rems = this.getRemisionesInfo(lote) || [];
    const nums = rems.map(r => r.numero_remision || r.numero_remision).filter(Boolean);
    return nums.length ? nums.join(', ') : '-';
  }

  getFechaEntrega(lote: Lote): string {
    // Preferir fecha almacenada en el lote
    if ((lote as any).fecha_entrega) {
      try { return new Date((lote as any).fecha_entrega).toLocaleString(); } catch { return '-'; }
    }
    const rems = this.getRemisionesInfo(lote);
    if (!rems || rems.length === 0) return '-';
    // fallback: prefer fecha_recepcion (real entrega) else fecha_remision
    const r = rems.find(r => r.fecha_recepcion) || rems[0];
    return r && r.fecha_recepcion ? (new Date(r.fecha_recepcion)).toLocaleString() : '-';
  }

  getFechaEstimada(lote: Lote): string {
    // Preferir fecha estimada almacenada en el lote
    if ((lote as any).fecha_entrega_estimada) {
      try { return new Date((lote as any).fecha_entrega_estimada).toLocaleString(); } catch { return '-'; }
    }
    const rems = this.getRemisionesInfo(lote);
    if (!rems || rems.length === 0) return '-';
    const r = rems[0];
    return r && r.fecha_entrega_estimada ? (new Date(r.fecha_entrega_estimada)).toLocaleString() : '-';
  }

  getDespacha(lote: Lote): string {
    // Preferir el booleano almacenado en el lote
    if (typeof (lote as any).despacha !== 'undefined' && (lote as any).despacha !== null) {
      return (lote as any).despacha ? 'Sí' : 'No';
    }
    const rems = this.getRemisionesInfo(lote);
    if (!rems || rems.length === 0) return '-';
    // mostrar nombre del taller que recibe/despacha como fallback
    const nombres = rems.map(r => r.taller?.nombre || r.taller_nombre || '').filter(Boolean);
    return nombres.length ? Array.from(new Set(nombres)).join(', ') : '-';
  }

  getConfeccionistas(lote: Lote): string {
    // Preferir el nombre almacenado directamente en el lote si existe
    if ((lote as any).confeccionista_nombre) {
      return (lote as any).confeccionista_nombre || '-';
    }
    const rems = this.getRemisionesInfo(lote);
    if (!rems || rems.length === 0) return '-';
    const nombres: string[] = [];
    rems.forEach(r => {
      (r.detalles || []).forEach((d: any) => {
        if (d.confeccionista_nombre) nombres.push(d.confeccionista_nombre);
      });
    });
    const uniq = Array.from(new Set(nombres)).filter(Boolean);
    return uniq.length ? uniq.join(', ') : '-';
  }

  getTotalLote(lote: Lote): number {
    if (lote.cantidad_total_programada) {
      return lote.cantidad_total_programada;
    }
    if (lote.detalles && lote.detalles.length > 0) {
      return lote.detalles.reduce((sum, d) => sum + (d.cantidad || 0), 0);
    }
    return 0;
  }
}

