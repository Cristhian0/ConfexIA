import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { InventarioTelaService } from '../../services/inventario-tela.service';
import { CatalogoService } from '../../services/catalogo.service';
import { CorteService, ReservaTela, ReservaTelaCreate } from '../../services/corte.service';
import { Color } from '../../models/color.model';
import { Material } from '../../models/material.model';
import { RolloStock, IngresoRolloCreate, SalidaRolloCreate, RolloMovimiento } from '../../models/inventario-tela.model';

@Component({
  selector: 'app-inventario-tela',
  templateUrl: './inventario-tela.component.html',
  styleUrls: ['./inventario-tela.component.scss']
})
export class InventarioTelaComponent implements OnInit {
  stock: RolloStock[] = [];
  movimientos: RolloMovimiento[] = [];
  reservas: ReservaTela[] = []; // RF-03: reservas de tela

  materiales: Material[] = [];
  colores: Color[] = [];

  loading = false;
  seeding = false;

  ingresoForm: FormGroup;
  salidaForm: FormGroup;
  filtroStockForm: FormGroup;
  filtroMovimientosForm: FormGroup;
  reservaForm: FormGroup; // RF-03: formulario para reservar tela

  constructor(
    private fb: FormBuilder,
    private inventarioTelaService: InventarioTelaService,
    private catalogoService: CatalogoService,
    private corteService: CorteService // RF-03: para gestionar reservas
  ) {
    this.ingresoForm = this.fb.group({
      material_id: ['', Validators.required],
      color_id: ['', Validators.required],
      lote_proveedor: ['', Validators.required],
      cantidad: [0, [Validators.required, Validators.min(0.01)]],
      descripcion: ['']
    });

    this.salidaForm = this.fb.group({
      orden_corte_id: [1, [Validators.required, Validators.min(1)]],
      material_id: ['', Validators.required],
      color_id: ['', Validators.required],
      cantidad: [0, [Validators.required, Validators.min(0.01)]],
      descripcion: ['']
    });

    this.filtroStockForm = this.fb.group({
      tipo: [''],
      color: [''],
      lote: ['']
    });

    this.filtroMovimientosForm = this.fb.group({
      orden_corte_id: ['']
    });

    this.reservaForm = this.fb.group({ // RF-03: formulario para reservar tela
      material_id: ['', [Validators.required]],
      color_id: ['', [Validators.required]],
      metros: ['', [Validators.required, Validators.min(0.01)]],
      orden_corte_id: [''],
      observaciones: ['']
    });
  }

  ngOnInit(): void {
    this.cargarCatalogos();
    this.cargarStock();
    this.cargarMovimientosInicial();
    this.cargarReservas(); // RF-03: cargar reservas de tela
  }

  cargarCatalogos(): void {
    this.catalogoService.listarMateriales(true).subscribe({
      next: (data) => (this.materiales = data || []),
      error: (e) => console.error('Error cargando materiales', e)
    });
    this.catalogoService.listarColores(true).subscribe({
      next: (data) => (this.colores = data || []),
      error: (e) => console.error('Error cargando colores', e)
    });
  }

  cargarStock(tipo?: string, color?: string, lote?: string): void {
    this.loading = true;
    this.inventarioTelaService.listarStock(tipo, color, lote).subscribe({
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

  cargarMovimientosInicial(): void {
    // Se carga historial reciente sin filtros
    this.inventarioTelaService.listarMovimientos().subscribe({
      next: (rows) => (this.movimientos = rows || []),
      error: (e) => console.error('Error cargando movimientos', e)
    });
  }

  agregarIngreso(): void {
    if (this.ingresoForm.invalid) return;

    const value = this.ingresoForm.value;
    const payload: IngresoRolloCreate = {
      material_id: Number(value.material_id),
      color_id: Number(value.color_id),
      lote_proveedor: value.lote_proveedor,
      cantidad: Number(value.cantidad),
      descripcion: value.descripcion || ''
    };

    this.inventarioTelaService.ingresarRollos(payload).subscribe({
      next: () => {
        alert('Ingreso de rollos registrado');
        this.cargarStock();
        this.cargarMovimientosInicial();
        this.ingresoForm.patchValue({ cantidad: 0, descripcion: '', lote_proveedor: '' });
      },
      error: (e) => {
        console.error('Error registrando ingreso', e);
        alert('Error registrando ingreso');
      }
    });
  }

  registrarSalida(): void {
    if (this.salidaForm.invalid) {
      alert('Por favor completa todos los campos requeridos correctamente');
      return;
    }

    // Validación adicional de stock disponible
    if (this.checkStockInsuficiente()) {
      const disponible = this.getStockDisponibleParaUso(
        this.salidaForm.value.material_id,
        this.salidaForm.value.color_id
      );
      alert(`Stock insuficiente. Solo hay ${disponible} metros disponibles para uso.`);
      return;
    }

    const value = this.salidaForm.value;
    const payload: SalidaRolloCreate = {
      material_id: parseInt(value.material_id, 10),
      color_id: parseInt(value.color_id, 10),
      cantidad: parseFloat(value.cantidad) || 0,
      orden_corte_id: value.orden_corte_id ? parseInt(value.orden_corte_id, 10) : undefined,
      descripcion: value.descripcion?.trim() || `Salida para Orden de Corte #${value.orden_corte_id}`
    };

    console.log('Enviando salida de rollos:', payload);

    this.loading = true;
    this.inventarioTelaService.sacarRollos(payload).subscribe({
      next: (movimiento) => {
        const materialNombre = this.getMaterialNombre(value.material_id);
        const colorNombre = this.getColorNombre(value.color_id);
        alert(`✅ Salida registrada exitosamente!\n\nMaterial: ${materialNombre}\nColor: ${colorNombre}\nCantidad: ${value.cantidad} metros\nOrden de Corte: #${value.orden_corte_id}`);

        this.cargarStock();
        this.cargarMovimientosInicial();
        this.limpiarSalidaForm();
        this.loading = false;
      },
      error: (e) => {
        console.error('Error registrando salida', e);
        this.loading = false;

        let errorMsg = 'Error desconocido al registrar la salida';
        if (e.error?.detail) {
          errorMsg = e.error.detail;
        } else if (e.status === 404) {
          errorMsg = 'No se encontró stock disponible para el material y color seleccionados';
        } else if (e.status === 400) {
          errorMsg = 'Datos inválidos. Verifica que la cantidad sea correcta';
        }

        alert(`❌ Error al registrar salida: ${errorMsg}`);
      }
    });
  }

  filtrarStock(): void {
    const { tipo, color, lote } = this.filtroStockForm.value;
    this.cargarStock(tipo || undefined, color || undefined, lote || undefined);
  }

  limpiarFiltroStock(): void {
    this.filtroStockForm.reset({ tipo: '', color: '', lote: '' });
    this.cargarStock();
  }

  filtrarMovimientos(): void {
    const orden_corte_id_raw = this.filtroMovimientosForm.value.orden_corte_id;
    const orden_corte_id = orden_corte_id_raw ? Number(orden_corte_id_raw) : undefined;

    this.inventarioTelaService.listarMovimientos(undefined, undefined, orden_corte_id).subscribe({
      next: (rows) => (this.movimientos = rows || []),
      error: (e) => console.error('Error filtrando movimientos', e)
    });
  }

  formatDate(date: string): string {
    return new Date(date).toLocaleDateString('es-ES');
  }

  cargarReservas(): void {
    this.corteService.listarReservas().subscribe({
      next: (data) => (this.reservas = data || []),
      error: (e) => console.error('Error cargando reservas', e)
    });
  }

  crearReserva(): void { // RF-03: reservar tela para producción
    if (this.reservaForm.invalid) {
      const errors = [];
      if (this.reservaForm.get('material_id')?.invalid) errors.push('Selecciona un material');
      if (this.reservaForm.get('color_id')?.invalid) errors.push('Selecciona un color');
      if (this.reservaForm.get('metros')?.invalid) {
        if (this.reservaForm.get('metros')?.hasError('required')) {
          errors.push('Ingresa la cantidad de metros');
        } else if (this.reservaForm.get('metros')?.hasError('min')) {
          errors.push('La cantidad debe ser mayor a 0');
        }
      }
      alert('Por favor completa los campos: ' + errors.join(', '));
      return;
    }

    const value = this.reservaForm.value;
    const metros = parseFloat(value.metros);
    
    if (metros <= 0) {
      alert('La cantidad de metros debe ser mayor a 0');
      return;
    }

    const reservaData: ReservaTelaCreate = {
      material_id: parseInt(value.material_id, 10),
      color_id: parseInt(value.color_id, 10),
      metros: metros,
      orden_corte_id: value.orden_corte_id ? parseInt(value.orden_corte_id, 10) : undefined,
      observaciones: value.observaciones?.trim() || undefined
    };

    console.log('Enviando reserva de tela:', reservaData);

    this.corteService.crearReserva(reservaData).subscribe({
      next: (reserva) => {
        this.reservas.unshift(reserva);
        this.cargarStock(); // Recargar stock para ver cantidad reservada actualizada
        this.reservaForm.reset();
        alert('Reserva de tela creada exitosamente');
      },
      error: (e) => {
        console.error('Error creando reserva', e);
        const errorMsg = e.error?.detail || e.statusText || 'Error desconocido';
        alert(`Error al crear la reserva de tela: ${errorMsg}`);
      }
    });
  }

  liberarReserva(reservaId: number): void { // RF-03: liberar reserva
    if (!confirm('¿Está seguro de liberar esta reserva? La tela volverá a estar disponible.')) return;

    this.corteService.liberarReserva(reservaId).subscribe({
      next: (reserva) => {
        const index = this.reservas.findIndex(r => r.id === reservaId);
        if (index !== -1) this.reservas[index] = reserva;
        this.cargarStock(); // Recargar stock para ver cantidad reservada actualizada
        alert('Reserva liberada exitosamente');
      },
      error: (e) => {
        console.error('Error liberando reserva', e);
        alert('Error al liberar la reserva');
      }
    });
  }

  consumirReserva(reservaId: number): void { // RF-03: consumir reserva (usada en producción)
    if (!confirm('¿Está seguro de consumir esta reserva? La tela será descontada del inventario.')) return;

    this.corteService.consumirReserva(reservaId).subscribe({
      next: (reserva) => {
        const index = this.reservas.findIndex(r => r.id === reservaId);
        if (index !== -1) this.reservas[index] = reserva;
        this.cargarStock(); // Recargar stock para ver cantidad actual actualizada
        this.cargarMovimientosInicial(); // Recargar historial de movimientos
        // Cargar movimientos específicos de este material-color
        if (reserva.material_id && reserva.color_id) {
          this.cargarMovimientosTela(reserva.material_id, reserva.color_id);
        }
        alert('Reserva consumida exitosamente');
      },
      error: (e) => {
        console.error('Error consumiendo reserva', e);
        alert('Error al consumir la reserva');
      }
    });
  }

  sembrarInventarioInicial(): void {
    if (!this.materiales.length || !this.colores.length) return;
    this.seeding = true;

    const buscar = (s: string, needle: string) => s.toLowerCase().includes(needle);

    const colorBlanco = this.colores.find((c) => buscar(c.nombre || '', 'blanco'));
    const colorNegro = this.colores.find((c) => buscar(c.nombre || '', 'negro'));
    const materialMelanina = this.materiales.find((m) => buscar(m.nombre || '', 'melanina'));
    const materialDefault = materialMelanina || this.materiales[0];

    if (!colorBlanco || !colorNegro || !materialDefault) {
      this.seeding = false;
      alert('No se encontraron "blanco"/"negro" o "melanina" en el catálogo. Selecciona manualmente en Ingreso de Rollos.');
      return;
    }

    // 20 blancas / 30 negras (asumiendo material melanina si existe; si no, el primer material del catalogo)
    const tareas = [
      {
        material_id: materialDefault.id,
        color_id: colorBlanco.id,
        cantidad: 20,
        descripcion: 'Inventario inicial'
      },
      {
        material_id: materialDefault.id,
        color_id: colorNegro.id,
        cantidad: 30,
        descripcion: 'Inventario inicial'
      }
    ] as IngresoRolloCreate[];

    this.inventarioTelaService.ingresarRollos(tareas[0]).subscribe({
      next: () => {
        this.inventarioTelaService.ingresarRollos(tareas[1]).subscribe({
          next: () => {
            alert('Inventario inicial registrado (20 blancas / 30 negras).');
            this.seeding = false;
            this.cargarStock();
            this.cargarMovimientosInicial();
          },
          error: (e) => {
            console.error('Error sembrando inventario inicial', e);
            this.seeding = false;
            alert('Error al registrar inventario inicial.');
          }
        });
      },
      error: (e) => {
        console.error('Error sembrando inventario inicial', e);
        this.seeding = false;
        alert('Error al registrar inventario inicial.');
      }
    });
  }

  cargarMovimientosTela(materialId: number, colorId: number): void {
    this.corteService.listarMovimientosTela(materialId, colorId).subscribe({
      next: (data) => {
        this.movimientos = data || [];
      },
      error: (e) => {
        console.error('Error cargando movimientos de tela', e);
        this.movimientos = [];
      }
    });
  }

  getMovementTypeClass(tipo: string): string {
    switch (tipo) {
      case 'INGRESO': return 'chip-success';
      case 'SALIDA': return 'chip-danger';
      case 'AJUSTE': return 'chip-warning';
      default: return 'chip-default';
    }
  }

  getQuantityClass(cantidad: number): string {
    return cantidad >= 0 ? 'quantity-positive' : 'quantity-negative';
  }

  // Métodos helper para la salida por orden de corte
  getStockDisponible(materialId: number, colorId: number): number {
    if (!materialId || !colorId) return 0;
    // Sumar todos los stocks disponibles para este material/color (múltiples lotes)
    return this.stock
      .filter(s => s.material_id === parseInt(materialId.toString()) && s.color_id === parseInt(colorId.toString()))
      .reduce((total, item) => total + item.cantidad_actual, 0);
  }

  getStockReservado(materialId: number, colorId: number): number {
    if (!materialId || !colorId) return 0;
    // Sumar todas las reservas para este material/color
    return this.stock
      .filter(s => s.material_id === parseInt(materialId.toString()) && s.color_id === parseInt(colorId.toString()))
      .reduce((total, item) => total + item.cantidad_reservada, 0);
  }

  getStockDisponibleParaUso(materialId: number, colorId: number): number {
    const disponible = this.getStockDisponible(materialId, colorId);
    const reservado = this.getStockReservado(materialId, colorId);
    return Math.max(0, disponible - reservado);
  }

  getMaterialNombre(materialId: number): string {
    if (!materialId) return '';
    const material = this.materiales.find(m => m.id === parseInt(materialId.toString()));
    return material ? material.nombre : '';
  }

  getColorNombre(colorId: number): string {
    if (!colorId) return '';
    const color = this.colores.find(c => c.id === parseInt(colorId.toString()));
    return color ? color.nombre : '';
  }

  onMaterialChange(): void {
    // Actualizar información del stock cuando cambia el material
    this.actualizarInfoStock();
  }

  onColorChange(): void {
    // Actualizar información del stock cuando cambia el color
    this.actualizarInfoStock();
  }

  actualizarInfoStock(): void {
    // Forzar actualización de la vista para mostrar información del stock
    const materialId = this.salidaForm.value.material_id;
    const colorId = this.salidaForm.value.color_id;
    if (materialId && colorId) {
      // La información se actualiza automáticamente en el template
    }
  }

  checkStockInsuficiente(): boolean {
    const formValue = this.salidaForm.value;
    if (!formValue.material_id || !formValue.color_id || !formValue.cantidad) return false;

    const disponibleParaUso = this.getStockDisponibleParaUso(formValue.material_id, formValue.color_id);
    return formValue.cantidad > disponibleParaUso;
  }

  limpiarSalidaForm(): void {
    this.salidaForm.reset({
      orden_corte_id: 1,
      material_id: '',
      color_id: '',
      cantidad: 0,
      descripcion: ''
    });
  }
}

