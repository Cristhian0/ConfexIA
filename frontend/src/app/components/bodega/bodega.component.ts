import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { BodegaService } from '../../services/bodega.service';
import { CatalogoService } from '../../services/catalogo.service';
import { Color } from '../../models/color.model';
import { Talla } from '../../models/talla.model';
import { ProductoTerminadoStock, ProductoTerminadoSalidaCreate, ZonaAlmacen } from '../../models/producto-terminado.model';
import { RemisionFormComponent } from '../remisiones/remision-form/remision-form.component';

interface CategoriaResumen {
  categoria: string;
  cantidad: number;
  items: number;
}

@Component({
  selector: 'app-bodega',
  templateUrl: './bodega.component.html',
  styleUrls: ['./bodega.component.scss']
})
export class BodegaComponent implements OnInit {
  stock: ProductoTerminadoStock[] = [];
  tallas: Talla[] = [];
  colores: Color[] = [];
  zonas = Object.values(ZonaAlmacen);

  filtroForm: FormGroup;
  salidaForm: FormGroup;

  selectedStock: ProductoTerminadoStock | null = null;
  loading = false;
  error = '';
  success = '';

  constructor(
    private fb: FormBuilder,
    private bodegaService: BodegaService,
    private catalogoService: CatalogoService,
    private dialog: MatDialog
  ) {
    this.filtroForm = this.fb.group({
      sku: [''],
      tipo: [''],
      talla_id: [''],
      color_id: [''],
      zona: ['']
    });

    this.salidaForm = this.fb.group({
      cantidad: [1, [Validators.required, Validators.min(1)]],
      descripcion: ['', Validators.maxLength(500)]
    });
  }

  ngOnInit(): void {
    this.cargarCatalogos();
    this.cargarStock();
  }

  cargarCatalogos(): void {
    this.catalogoService.listarTallas().subscribe({
      next: (data) => this.tallas = data || [],
      error: (e) => console.error('Error cargando tallas', e)
    });

    this.catalogoService.listarColores(true).subscribe({
      next: (data) => this.colores = data || [],
      error: (e) => console.error('Error cargando colores', e)
    });
  }

  cargarStock(): void {
    this.loading = true;
    const values = this.filtroForm.value;
    const zona = values.zona || undefined;

    this.bodegaService.listarStock(
      values.sku || undefined,
      values.tipo || undefined,
      values.talla_id ? Number(values.talla_id) : undefined,
      values.color_id ? Number(values.color_id) : undefined,
      zona as string | undefined
    ).subscribe({
      next: (data) => {
        this.stock = data || [];
        this.loading = false;
      },
      error: (error) => {
        console.error('Error cargando stock de bodega', error);
        this.error = 'Error cargando stock de bodega';
        this.loading = false;
      }
    });
  }

  buscarStock(): void {
    this.cargarStock();
  }

  limpiarFiltros(): void {
    this.filtroForm.reset({ sku: '', tipo: '', talla_id: '', color_id: '', zona: '' });
    this.cargarStock();
  }

  seleccionarStock(item: ProductoTerminadoStock): void {
    this.selectedStock = item;
    this.salidaForm.patchValue({ cantidad: 1, descripcion: '' });
    this.error = '';
    this.success = '';
  }

  registrarSalida(): void {
    if (!this.selectedStock || this.salidaForm.invalid) {
      return;
    }

    this.loading = true;
    const payload: ProductoTerminadoSalidaCreate = {
      cantidad: Number(this.salidaForm.value.cantidad),
      descripcion: this.salidaForm.value.descripcion || `Remisión de ${this.selectedStock.sku}`
    };

    this.bodegaService.registrarSalida(this.selectedStock.id, payload).subscribe({
      next: (updatedStock) => {
        this.success = 'Salida registrada correctamente';
        this.error = '';
        this.selectedStock = updatedStock;
        this.cargarStock();
        this.loading = false;
        setTimeout(() => this.success = '', 3000);
      },
      error: (error) => {
        console.error('Error registrando salida', error);
        this.error = error?.error?.detail || 'Error al registrar la remisión';
        this.success = '';
        this.loading = false;
      }
    });
  }

  abrirRemisionRapida(item: ProductoTerminadoStock): void {
    const dialogRef = this.dialog.open(RemisionFormComponent, {
      width: '960px',
      data: {
        stockItem: {
          tipo_prenda: item.tipo,
          talla_id: item.talla_id,
          cantidad: item.cantidad_actual,
          descripcion: `Remisión rápida de ${item.tipo} ${item.sku}`
        }
      }
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.cargarStock();
      }
    });
  }

  cerrarDetalle(): void {
    this.selectedStock = null;
    this.salidaForm.reset({ cantidad: 1, descripcion: '' });
  }

  getNombreTalla(tallaId: number): string {
    const talla = this.tallas.find((item) => item.id === tallaId);
    return talla ? talla.nombre : `ID: ${tallaId}`;
  }

  getNombreColor(colorId: number): string {
    const color = this.colores.find((item) => item.id === colorId);
    return color ? color.nombre : `ID: ${colorId}`;
  }

  get totalStock(): number {
    return this.stock.reduce((sum, item) => sum + item.cantidad_actual, 0);
  }

  get resumenCategorias(): CategoriaResumen[] {
    const segmentos: { [key: string]: { cantidad: number; items: number } } = {};

    this.stock.forEach(item => {
      const categoria = this.obtenerCategoria(item.tipo);
      if (!segmentos[categoria]) {
        segmentos[categoria] = { cantidad: 0, items: 0 };
      }
      segmentos[categoria].cantidad += item.cantidad_actual;
      segmentos[categoria].items += 1;
    });

    return Object.entries(segmentos).map(([categoria, datos]) => ({
      categoria,
      cantidad: datos.cantidad,
      items: datos.items
    })).sort((a, b) => b.cantidad - a.cantidad);
  }

  obtenerCategoria(tipo: string): string {
    const valor = tipo.toLowerCase();
    if (valor.includes('camis') || valor.includes('shirt')) {
      return 'Camisas';
    }
    if (valor.includes('pantal') || valor.includes('pant')) {
      return 'Pantalones';
    }
    if (valor.includes('chaqueta') || valor.includes('saco') || valor.includes('blazer')) {
      return 'Chaquetas';
    }
    if (valor.includes('vestido') || valor.includes('falda') || valor.includes('dress')) {
      return 'Vestidos';
    }
    return 'Otros';
  }
}
