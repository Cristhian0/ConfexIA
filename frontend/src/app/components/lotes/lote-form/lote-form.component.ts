import { Component, OnInit, Inject, ViewEncapsulation } from '@angular/core';
import { FormBuilder, FormGroup, Validators, FormArray } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { LoteService } from '../../../services/lote.service';
import { CatalogoService } from '../../../services/catalogo.service';
import { CorteService } from '../../../services/corte.service';
import { Lote, LoteCreate, LoteUpdate, LoteDetalleCreate, OrdenCorteBasica } from '../../../models/lote.model';
import { Talla } from '../../../models/talla.model';
import { Color } from '../../../models/color.model';
import { Material } from '../../../models/material.model';
import { Referencia } from '../../../models/referencia.model';

@Component({
  selector: 'app-lote-form',
  templateUrl: './lote-form.component.html',
  styleUrls: ['./lote-form.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class LoteFormComponent implements OnInit {
  form!: FormGroup;
  tallas: Talla[] = [];
  colores: Color[] = [];
  materiales: Material[] = [];
  referencias: Referencia[] = [];
  ordenesCorte: OrdenCorteBasica[] = [];
  isEdit = false;

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<LoteFormComponent>,
    @Inject(MAT_DIALOG_DATA) public data: Lote | null,
    private loteService: LoteService,
    private catalogoService: CatalogoService,
    private corteService: CorteService,
    private snackBar: MatSnackBar
  ) {
    this.inicializarFormulario();
  }

  inicializarFormulario(): void {
    this.form = this.fb.group({
      numero_lote: ['', Validators.required],
      mesa: [''],
      remision_numero: [''],
      confeccionista_nombre: [''],
      referencia_nombre: ['', Validators.required],
      material_nombre: ['', Validators.required],
      orden_corte_id: [null],  // Asociación opcional con orden de corte
      fecha_corte: ['', Validators.required],
      fecha_entrega: [''],
      fecha_entrega_estimada: [''],
      despacha: [false],
      observaciones: [''],
      es_pedido_especial: [false],
      prioridad: [0],
      cantidad_total_programada: [0],
      detalles: this.fb.array([])
    });
  }

  ngOnInit(): void {
    this.inicializarFormulario();
    this.cargarCatalogos();
    this.cargarOrdenesCorte();
    if (this.data) {
      this.isEdit = true;
      this.cargarDatos();
    } else {
      this.agregarDetalle();
    }
    // Actualizar total después de cargar datos
    setTimeout(() => this.actualizarTotal(), 200);
  }

  cargarDatos(): void {
    if (this.data) {
      // Convertir fecha_corte a formato para mat-datepicker (si viene como ISO string)
      let fechaCorte = this.data.fecha_corte;
      if (fechaCorte && typeof fechaCorte === 'string') {
        fechaCorte = fechaCorte.split('T')[0]; // Para input type="date"
      }

      this.form.patchValue({
        numero_lote: this.data.numero_lote,
        mesa: this.data.mesa,
        remision_numero: this.data.remision_numero,
        confeccionista_nombre: this.data.confeccionista_nombre,
        referencia_nombre: this.data.referencia_nombre,
        material_nombre: this.data.material_nombre,
        orden_corte_id: this.data.orden_corte_id,
        fecha_corte: fechaCorte,
        fecha_entrega: this.data.fecha_entrega,
        fecha_entrega_estimada: this.data.fecha_entrega_estimada,
        despacha: this.data.despacha,
        observaciones: this.data.observaciones,
        es_pedido_especial: this.data.es_pedido_especial,
        prioridad: this.data.prioridad,
        cantidad_total_programada: this.data.cantidad_total_programada
      });

      // Limpiar detalles existentes y cargar los del lote
      while (this.detalles.length > 0) {
        this.detalles.removeAt(0);
      }

      // Agregar los detalles del lote
      this.data.detalles.forEach(detalle => {
        this.agregarDetalle(
          detalle.color_nombre,
          detalle.talla_id,
          detalle.cantidad
        );
      });
    }
  }

  cargarCatalogos(): void {
    // Datos de prueba por defecto para asegurar que siempre haya opciones disponibles
    this.referencias = [
      { id: 1, codigo: 'CAM-001', nombre: 'Camiseta Básica', descripcion: 'Camiseta manga corta básica', es_pedido_especial: false, activo: true, created_at: new Date().toISOString() },
      { id: 2, codigo: 'CAM-002', nombre: 'Camiseta Polo', descripcion: 'Camiseta tipo polo', es_pedido_especial: false, activo: true, created_at: new Date().toISOString() },
      { id: 3, codigo: 'PANT-001', nombre: 'Pantalón Clásico', descripcion: 'Pantalón de vestir clásico', es_pedido_especial: false, activo: true, created_at: new Date().toISOString() },
      { id: 4, codigo: 'PANT-002', nombre: 'Jeans', descripcion: 'Pantalón jean', es_pedido_especial: false, activo: true, created_at: new Date().toISOString() },
      { id: 5, codigo: 'CHAQ-001', nombre: 'Chaqueta', descripcion: 'Chaqueta deportiva', es_pedido_especial: false, activo: true, created_at: new Date().toISOString() },
      { id: 6, codigo: 'ESP-001', nombre: 'Pedido Especial', descripcion: 'Referencia para pedidos especiales', es_pedido_especial: true, activo: true, created_at: new Date().toISOString() }
    ];

    this.materiales = [
      { id: 1, codigo: 'ALG', nombre: 'Algodón', descripcion: '100% Algodón', activo: true, created_at: new Date().toISOString() },
      { id: 2, codigo: 'POL', nombre: 'Poliéster', descripcion: '100% Poliéster', activo: true, created_at: new Date().toISOString() },
      { id: 3, codigo: 'ALG-POL', nombre: 'Algodón-Poliéster', descripcion: 'Mezcla 60/40', activo: true, created_at: new Date().toISOString() },
      { id: 4, codigo: 'LYC', nombre: 'Licra', descripcion: 'Material elástico', activo: true, created_at: new Date().toISOString() },
      { id: 5, codigo: 'DEN', nombre: 'Denim', descripcion: 'Mezclilla', activo: true, created_at: new Date().toISOString() }
    ];

    this.tallas = [
      { id: 1, codigo: 'XS', nombre: 'Extra Small', activo: true, created_at: new Date().toISOString() },
      { id: 2, codigo: 'S', nombre: 'Small', activo: true, created_at: new Date().toISOString() },
      { id: 3, codigo: 'M', nombre: 'Medium', activo: true, created_at: new Date().toISOString() },
      { id: 4, codigo: 'L', nombre: 'Large', activo: true, created_at: new Date().toISOString() },
      { id: 5, codigo: 'XL', nombre: 'Extra Large', activo: true, created_at: new Date().toISOString() },
      { id: 6, codigo: 'XXL', nombre: 'Double Extra Large', activo: true, created_at: new Date().toISOString() }
    ];

    this.colores = [
      { id: 1, codigo: 'BLK', nombre: 'Negro', activo: true, created_at: new Date().toISOString() },
      { id: 2, codigo: 'WHT', nombre: 'Blanco', activo: true, created_at: new Date().toISOString() },
      { id: 3, codigo: 'GRY', nombre: 'Gris', activo: true, created_at: new Date().toISOString() },
      { id: 4, codigo: 'BLU', nombre: 'Azul', activo: true, created_at: new Date().toISOString() },
      { id: 5, codigo: 'RED', nombre: 'Rojo', activo: true, created_at: new Date().toISOString() },
      { id: 6, codigo: 'NAV', nombre: 'Azul Marino', activo: true, created_at: new Date().toISOString() }
    ];

    // Intentar cargar desde el servidor y reemplazar si hay datos
    this.catalogoService.listarTallas(true).subscribe({
      next: (data) => {
        if (data && data.length > 0) {
          this.tallas = data;
          console.log(`Tallas cargadas desde servidor: ${this.tallas.length}`);
        }
      },
      error: (error) => {
        console.error('Error cargando tallas:', error);
        // Mantener datos de prueba
      }
    });

    this.catalogoService.listarColores(true).subscribe({
      next: (data) => {
        if (data && data.length > 0) {
          this.colores = data;
          console.log(`Colores cargados desde servidor: ${this.colores.length}`);
        }
      },
      error: (error) => {
        console.error('Error cargando colores:', error);
        // Mantener datos de prueba
      }
    });

    this.catalogoService.listarMateriales(true).subscribe({
      next: (data) => {
        if (data && data.length > 0) {
          this.materiales = data;
          console.log(`Materiales cargados desde servidor: ${this.materiales.length}`);
        }
      },
      error: (error) => {
        console.error('Error cargando materiales:', error);
        // Mantener datos de prueba
      }
    });

    this.catalogoService.listarReferencias(true).subscribe({
      next: (data) => {
        if (data && data.length > 0) {
          this.referencias = data;
          console.log(`Referencias cargadas desde servidor: ${this.referencias.length}`);
        }
      },
      error: (error) => {
        console.error('Error cargando referencias:', error);
        // Mantener datos de prueba
      }
    });
  }

  cargarOrdenesCorte(): void {
    this.corteService.listarOrdenes().subscribe({
      next: (data) => {
        // Filtrar solo órdenes que estén en estado 'cortado' o 'cerrado' para asociar a lotes
        this.ordenesCorte = data.filter(orden => 
          orden.estado === 'cortado' || orden.estado === 'cerrado'
        ).map(orden => ({
          id: orden.id,
          numero_orden: orden.numero_orden,
          tipo_prenda: orden.tipo_prenda,
          estado: orden.estado,
          fecha_creacion: orden.created_at
        }));
        console.log(`Órdenes de corte disponibles: ${this.ordenesCorte.length}`);
      },
      error: (error) => {
        console.error('Error cargando órdenes de corte:', error);
        this.ordenesCorte = [];
      }
    });
  }

  get detalles(): FormArray {
    return this.form.get('detalles') as FormArray;
  }

  agregarDetalle(colorNombre?: string, tallaId?: number, cantidad?: number): void {
    const detalleForm = this.fb.group({
      color_nombre: [colorNombre || '', Validators.required],
      talla_id: [tallaId || null, Validators.required],
      cantidad: [cantidad || 0, [Validators.required, Validators.min(1)]]
    });
    this.detalles.push(detalleForm);
    // Actualizar total después de agregar
    this.actualizarTotal();
    // Suscribirse a cambios en cantidad
    detalleForm.get('cantidad')?.valueChanges.subscribe(() => {
      this.actualizarTotal();
    });
  }

  eliminarDetalle(index: number): void {
    this.detalles.removeAt(index);
    this.actualizarTotal();
  }

  guardar(): void {
    console.log('DEBUG - Función guardar() llamada');
    console.log('DEBUG - Form exists:', !!this.form);
    console.log('DEBUG - Form value:', this.form?.value);
    
    if (!this.form) {
      console.error('Error: Formulario no inicializado');
      this.snackBar.open('Error: Formulario no inicializado', 'Cerrar', { duration: 3000 });
      return;
    }
    
    const formValue = this.form.value;
    if (!formValue) {
      console.error('Error: Datos del formulario no disponibles');
      this.snackBar.open('Error: Datos del formulario no disponibles', 'Cerrar', { duration: 3000 });
      return;
    }
    
    console.log('DEBUG - Form valid:', this.form.valid);
    console.log('DEBUG - Form value:', formValue);
    console.log('DEBUG - Detalles length:', this.detalles.length);
    
    if (this.form.valid) {
      console.log('DEBUG - Formulario válido, procediendo...');
      const formValue = this.form.value;
      
      // Validar que haya al menos un detalle
      if (this.detalles.length === 0) {
        console.log('DEBUG - No hay detalles, mostrando mensaje');
        this.snackBar.open('Debe agregar al menos una talla', 'Cerrar', { duration: 3000 });
        return;
      }

      console.log('DEBUG - Hay detalles, procesando datos...');

      // Calcular cantidad total si no se proporciona
      const cantidadTotal = formValue.cantidad_total_programada || 
        formValue.detalles.reduce((sum: number, d: any) => sum + parseInt(d.cantidad || 0, 10), 0);

      // Preparar detalles una sola vez para reutilizar
      const detallesData = formValue.detalles.map((d: any) => ({
        color_nombre: d.color_nombre || '',
        talla_id: d.talla_id,
        cantidad: parseInt(d.cantidad, 10)
      }));

      // Validar que referencia y material estén seleccionados
      let referenciaNombre = formValue.referencia_nombre;
      let materialNombre = formValue.material_nombre;
      
      console.log('DEBUG - Valores del formulario:', {
        referencia_nombre: referenciaNombre,
        material_nombre: materialNombre,
        tipo_referencia: typeof referenciaNombre,
        tipo_material: typeof materialNombre,
        referencias_disponibles: this.referencias.map(r => ({ id: r.id, nombre: r.nombre })),
        materiales_disponibles: this.materiales.map(m => ({ id: m.id, nombre: m.nombre }))
      });
      
      // Si viene como número (ID), buscar el nombre en los catálogos
      // También verificar si es un string que representa un número
      if (referenciaNombre) {
        let refId: number | null = null;
        if (typeof referenciaNombre === 'number') {
          refId = referenciaNombre;
        } else if (typeof referenciaNombre === 'string' && !isNaN(Number(referenciaNombre)) && referenciaNombre.trim() !== '') {
          refId = parseInt(referenciaNombre, 10);
        }
        
        if (refId !== null) {
          const ref = this.referencias.find(r => r.id === refId);
          if (ref) {
            referenciaNombre = ref.nombre;
            console.log(`DEBUG - Referencia convertida de ID ${refId} a nombre: ${referenciaNombre}`);
          } else {
            console.warn(`DEBUG - No se encontró referencia con ID: ${refId} en catálogos locales`);
          }
        }
      }
      
      if (materialNombre) {
        let matId: number | null = null;
        if (typeof materialNombre === 'number') {
          matId = materialNombre;
        } else if (typeof materialNombre === 'string' && !isNaN(Number(materialNombre)) && materialNombre.trim() !== '') {
          matId = parseInt(materialNombre, 10);
        }
        
        if (matId !== null) {
          const mat = this.materiales.find(m => m.id === matId);
          if (mat) {
            materialNombre = mat.nombre;
            console.log(`DEBUG - Material convertido de ID ${matId} a nombre: ${materialNombre}`);
          } else {
            console.warn(`DEBUG - No se encontró material con ID: ${matId} en catálogos locales`);
          }
        }
      }
      
      // Convertir a string y validar
      referenciaNombre = String(referenciaNombre || '').trim();
      materialNombre = String(materialNombre || '').trim();
      
      console.log('DEBUG - Nombres finales a enviar:', {
        referencia_nombre: referenciaNombre,
        material_nombre: materialNombre
      });
      
      if (!referenciaNombre) {
        this.snackBar.open('Debe seleccionar una referencia', 'Cerrar', { duration: 3000 });
        return;
      }
      
      if (!materialNombre) {
        this.snackBar.open('Debe seleccionar un material', 'Cerrar', { duration: 3000 });
        return;
      }

      const loteData: LoteCreate = {
        numero_lote: formValue.numero_lote,
        mesa: formValue.mesa || undefined,
        remision_numero: formValue.remision_numero || undefined,
        confeccionista_nombre: formValue.confeccionista_nombre || undefined,
        referencia_nombre: referenciaNombre,
        material_nombre: materialNombre,
        fecha_corte: formValue.fecha_corte ? new Date(formValue.fecha_corte).toISOString() : new Date().toISOString(),
        fecha_entrega: formValue.fecha_entrega ? new Date(formValue.fecha_entrega).toISOString() : undefined,
        fecha_entrega_estimada: formValue.fecha_entrega_estimada ? new Date(formValue.fecha_entrega_estimada).toISOString() : undefined,
        despacha: !!formValue.despacha,
        observaciones: formValue.observaciones || '',
        es_pedido_especial: formValue.es_pedido_especial || false,
        prioridad: formValue.prioridad || 0,
        cantidad_total_programada: cantidadTotal,
        detalles: detallesData
      };

      if (this.isEdit && this.data) {
        // Para actualizar, usar LoteUpdate con detalles (ya tenemos referenciaNombre y materialNombre convertidos)
        const loteUpdateData: LoteUpdate = {
          numero_lote: formValue.numero_lote,
          mesa: formValue.mesa || undefined,
          remision_numero: formValue.remision_numero || undefined,
          confeccionista_nombre: formValue.confeccionista_nombre || undefined,
          referencia_nombre: referenciaNombre,
          material_nombre: materialNombre,
          fecha_corte: formValue.fecha_corte ? new Date(formValue.fecha_corte).toISOString() : undefined,
          fecha_entrega: formValue.fecha_entrega ? new Date(formValue.fecha_entrega).toISOString() : undefined,
          fecha_entrega_estimada: formValue.fecha_entrega_estimada ? new Date(formValue.fecha_entrega_estimada).toISOString() : undefined,
          despacha: typeof formValue.despacha !== 'undefined' ? !!formValue.despacha : undefined,
          observaciones: formValue.observaciones || undefined,
          es_pedido_especial: formValue.es_pedido_especial || false,
          prioridad: formValue.prioridad || 0,
          cantidad_total_programada: cantidadTotal,
          detalles: detallesData  // Incluir detalles en la actualización
        };
        
        this.loteService.actualizar(this.data.id, loteUpdateData).subscribe({
          next: () => {
            this.snackBar.open('Lote actualizado correctamente', 'Cerrar', { duration: 3000 });
            this.dialogRef.close(true);
          },
          error: (error) => {
            console.error('Error actualizando lote:', error);
            const mensaje = error.error?.detail || error.message || 'Error al actualizar lote';
            this.snackBar.open(mensaje, 'Cerrar', { duration: 5000 });
          }
        });
      } else {
        // Para crear, usar LoteCreate (ya validado arriba)
        const loteCreateData: LoteCreate = loteData;
        
        console.log('Datos a enviar:', loteCreateData);
        this.loteService.crear(loteCreateData).subscribe({
          next: (response) => {
            console.log('DEBUG - Respuesta exitosa del backend:', response);
            this.snackBar.open('Lote creado correctamente', 'Cerrar', { duration: 3000 });
            this.dialogRef.close(true);
          },
          error: (error) => {
            console.error('DEBUG - Error del backend:', error);
            console.error('DEBUG - Detalles del error:', error.error);
            const mensaje = error.error?.detail || error.message || 'Error al crear lote';
            this.snackBar.open(mensaje, 'Cerrar', { duration: 7000 });
          }
        });
      }
    } else {
      // Mostrar qué campos están inválidos
      Object.keys(this.form.controls).forEach(key => {
        const control = this.form.get(key);
        if (control && control.invalid) {
          console.log(`Campo ${key} es inválido:`, control.errors);
        }
      });
      this.snackBar.open('Por favor complete todos los campos requeridos', 'Cerrar', { duration: 3000 });
    }
  }

  cancelar(): void {
    this.dialogRef.close();
  }

  calcularTotal(): number {
    if (!this.detalles || this.detalles.length === 0) {
      return 0;
    }
    let total = 0;
    this.detalles.controls.forEach(control => {
      const cantidad = control.get('cantidad')?.value;
      if (cantidad) {
        total += parseInt(cantidad.toString(), 10) || 0;
      }
    });
    return total;
  }

  actualizarTotal(): void {
    const total = this.calcularTotal();
    const control = this.form.get('cantidad_total_programada');
    if (control) {
      control.setValue(total, { emitEvent: false });
    }
  }

  getTallaNombre(tallaId: number): string {
    const talla = this.tallas.find(t => t.id === tallaId);
    return talla ? talla.nombre : '';
  }

  getTotalesPorTalla(): { talla: string, total: number }[] {
    const totales: { [key: number]: number } = {};
    this.detalles.controls.forEach(control => {
      const tallaId = control.get('talla_id')?.value;
      const cantidad = control.get('cantidad')?.value;
      if (tallaId && cantidad) {
        totales[tallaId] = (totales[tallaId] || 0) + parseInt(cantidad.toString(), 10);
      }
    });
    return Object.keys(totales).map(tallaId => ({
      talla: this.getTallaNombre(parseInt(tallaId, 10)),
      total: totales[parseInt(tallaId, 10)]
    }));
  }
}

