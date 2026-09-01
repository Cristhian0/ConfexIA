import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ProductoTerminadoService } from '../../services/producto-terminado.service';
import { CatalogoService } from '../../services/catalogo.service';
import { Color } from '../../models/color.model';
import { Talla } from '../../models/talla.model';
import {
  ProductoTerminadoStock,
  ProductoTerminadoStockCreate,
  ProductoTerminadoStockUpdate,
  ProductoTerminadoMovimiento,
  ZonaAlmacen
} from '../../models/producto-terminado.model';

@Component({
  selector: 'app-producto-terminado',
  templateUrl: './producto-terminado.component.html',
  styleUrls: ['./producto-terminado.component.scss']
})
export class ProductoTerminadoComponent implements OnInit {
  stock: ProductoTerminadoStock[] = [];
  movimientos: ProductoTerminadoMovimiento[] = [];

  tallas: Talla[] = [];
  colores: Color[] = [];
  zonas = Object.values(ZonaAlmacen);

  ingresoForm: FormGroup;
  filtroForm: FormGroup;
  selectedStock: ProductoTerminadoStock | null = null;

  loading = false;
  error = '';
  success = '';

  constructor(
    private fb: FormBuilder,
    private productoTerminadoService: ProductoTerminadoService,
    private catalogoService: CatalogoService
  ) {
    this.ingresoForm = this.fb.group({
      sku: ['', [Validators.required, Validators.maxLength(100)]],
      tipo: ['', [Validators.required, Validators.maxLength(100)]],
      talla_id: ['', Validators.required],
      color_id: ['', Validators.required],
      zona: [ZonaAlmacen.A1, Validators.required],
      cantidad_actual: [1, [Validators.required, Validators.min(1)]],
      descripcion: ['']
    });

    this.filtroForm = this.fb.group({
      sku: [''],
      tipo: [''],
      talla_id: [''],
      color_id: [''],
      zona: ['']
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

    this.productoTerminadoService.listarStock(
      values.sku || undefined,
      values.tipo || undefined,
      values.talla_id ? Number(values.talla_id) : undefined,
      values.color_id ? Number(values.color_id) : undefined,
      zona as ZonaAlmacen | undefined
    ).subscribe({
      next: (data) => {
        this.stock = data || [];
        this.loading = false;
      },
      error: (e) => {
        console.error('Error cargando stock', e);
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

  registrarIngreso(): void {
    if (this.ingresoForm.invalid) return;

    this.loading = true;
    const value = this.ingresoForm.value;
    const payload: ProductoTerminadoStockCreate = {
      sku: value.sku,
      tipo: value.tipo,
      talla_id: Number(value.talla_id),
      color_id: Number(value.color_id),
      zona: value.zona,
      cantidad_actual: Number(value.cantidad_actual),
      descripcion: value.descripcion || ''
    };

    this.productoTerminadoService.ingresarStock(payload).subscribe({
      next: () => {
        this.success = 'Ingreso registrado correctamente';
        this.error = '';
        this.ingresoForm.patchValue({ cantidad_actual: 1, descripcion: '' });
        this.cargarStock();
        this.loading = false;
        setTimeout(() => this.success = '', 3000);
      },
      error: (e) => {
        this.error = 'Error al registrar ingreso';
        this.success = '';
        console.error('Error ingresando stock', e);
        this.loading = false;
      }
    });
  }

  seleccionarStock(item: ProductoTerminadoStock): void {
    this.selectedStock = item;
    this.cargarMovimientos(item.id);
  }

  cargarMovimientos(stockId: number): void {
    this.productoTerminadoService.listarMovimientos(stockId).subscribe({
      next: (data) => this.movimientos = data || [],
      error: (e) => console.error('Error cargando movimientos', e)
    });
  }

  cerrarDetalle(): void {
    this.selectedStock = null;
    this.movimientos = [];
  }

  actualizarZona(zona: ZonaAlmacen | string): void {
    if (!this.selectedStock) return;

    const payload: ProductoTerminadoStockUpdate = { zona: zona as ZonaAlmacen };
    this.productoTerminadoService.actualizarStock(this.selectedStock.id, payload).subscribe({
      next: (data) => {
        this.selectedStock = data;
        this.success = 'Zona actualizada correctamente';
        setTimeout(() => this.success = '', 3000);
      },
      error: (e) => {
        this.error = 'Error al actualizar zona';
        console.error('Error actualizando zona', e);
      }
    });
  }
}
