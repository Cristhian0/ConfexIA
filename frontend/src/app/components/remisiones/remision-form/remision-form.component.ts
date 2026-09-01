import { Component, OnInit, Inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators, FormArray } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { TallerService } from '../../../services/taller.service';
import { LoteService } from '../../../services/lote.service';
import { Remision, RemisionCreate, RemisionDetalleCreate } from '../../../models/taller.model';
import { Taller } from '../../../models/taller.model';
import { Lote } from '../../../models/lote.model';
import { Talla } from '../../../models/talla.model';
import { CatalogoService } from '../../../services/catalogo.service';

export type RemisionFormData =
  | Remision
  | { tallerPreSeleccionado?: any; stockItem?: { tipo_prenda?: string; talla_id?: number; cantidad?: number; descripcion?: string } }
  | null;

@Component({
  selector: 'app-remision-form',
  templateUrl: './remision-form.component.html',
  styleUrls: ['./remision-form.component.scss']
})
export class RemisionFormComponent implements OnInit {
  form: FormGroup;
  talleres: Taller[] = [];
  lotes: Lote[] = [];
  tallas: Talla[] = [];
  isEdit = false;

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<RemisionFormComponent>,
    @Inject(MAT_DIALOG_DATA) public data: RemisionFormData,
    private tallerService: TallerService,
    private loteService: LoteService,
    private catalogoService: CatalogoService,
    private snackBar: MatSnackBar
  ) {
    this.form = this.fb.group({
      numero_remision: ['', Validators.required],
      lote_id: ['', Validators.required],
      taller_id: ['', Validators.required],
      fecha_remision: ['', Validators.required],
      fecha_entrega_estimada: [''],
      observaciones: [''],
      detalles: this.fb.array([])
    });
  }

  ngOnInit(): void {
    this.cargarDatos();
    
    if (this.isRemision(this.data)) {
      // Es una Remision existente (modo edición)
      this.isEdit = true;
      this.cargarDatosRemision(this.data as Remision);
    } else if (this.data && 'stockItem' in this.data && this.data.stockItem) {
      const stockItem = this.data.stockItem;
      this.agregarDetalle(
        stockItem.talla_id,
        stockItem.cantidad,
        undefined,
        stockItem.tipo_prenda,
        undefined
      );
      this.form.patchValue({ observaciones: stockItem.descripcion || '' });
    } else if (this.data && 'tallerPreSeleccionado' in this.data) {
      const dataWithTaller = this.data as { tallerPreSeleccionado: any };
      this.agregarDetalle();
      setTimeout(() => {
        if (dataWithTaller.tallerPreSeleccionado) {
          this.form.patchValue({
            taller_id: dataWithTaller.tallerPreSeleccionado.id
          });
        }
      }, 500);
    } else {
      this.agregarDetalle();
    }
  }

  cargarDatos(): void {
    // Datos de ejemplo para talleres
    this.talleres = [
      { id: 1, codigo: 'TALL-001', nombre: 'Taller Principal', direccion: 'Calle 123', telefono: '3001234567', contacto: 'Juan Pérez', activo: true, capacidad_diaria: 100, created_at: new Date().toISOString() },
      { id: 2, codigo: 'TALL-002', nombre: 'Taller Secundario', direccion: 'Calle 456', telefono: '3007654321', contacto: 'María García', activo: true, capacidad_diaria: 80, created_at: new Date().toISOString() },
      { id: 3, codigo: 'TALL-003', nombre: 'Taller Norte', direccion: 'Avenida Norte 789', telefono: '3009876543', contacto: 'Carlos López', activo: true, capacidad_diaria: 120, created_at: new Date().toISOString() }
    ];

    // Datos de ejemplo para tallas
    this.tallas = [
      { id: 1, codigo: 'XS', nombre: 'Extra Small', activo: true, created_at: new Date().toISOString() },
      { id: 2, codigo: 'S', nombre: 'Small', activo: true, created_at: new Date().toISOString() },
      { id: 3, codigo: 'M', nombre: 'Medium', activo: true, created_at: new Date().toISOString() },
      { id: 4, codigo: 'L', nombre: 'Large', activo: true, created_at: new Date().toISOString() },
      { id: 5, codigo: 'XL', nombre: 'Extra Large', activo: true, created_at: new Date().toISOString() }
    ];

    // Intentar cargar desde el servidor
    this.tallerService.listar(true).subscribe({
      next: (data) => {
        if (data && data.length > 0) {
          this.talleres = data;
        }
      },
      error: () => {
        console.log('Usando datos de ejemplo para talleres');
      }
    });

    this.loteService.listar().subscribe({
      next: (data) => {
        this.lotes = data;
      },
      error: (error) => {
        console.error('Error cargando lotes:', error);
        this.snackBar.open('Error al cargar lotes', 'Cerrar', { duration: 3000 });
      }
    });

    this.catalogoService.listarTallas(true).subscribe({
      next: (data) => {
        if (data && data.length > 0) {
          this.tallas = data;
        }
      },
      error: () => {
        console.log('Usando datos de ejemplo para tallas');
      }
    });
  }

  cargarDatosRemision(remision?: Remision): void {
    const dataRemision = remision || (this.data as Remision);
    if (dataRemision && 'id' in dataRemision) {
      // Convertir fecha_remision a formato para mat-datepicker (si viene como ISO string)
      let fechaRemision = dataRemision.fecha_remision;
      if (fechaRemision && typeof fechaRemision === 'string') {
        fechaRemision = fechaRemision.split('T')[0]; // Para input type="date"
      }
      
      let fechaEntregaEstimada = dataRemision.fecha_entrega_estimada;
      if (fechaEntregaEstimada && typeof fechaEntregaEstimada === 'string') {
        fechaEntregaEstimada = fechaEntregaEstimada.split('T')[0]; // Para input type="date"
      }

      this.form.patchValue({
        numero_remision: dataRemision.numero_remision,
        lote_id: dataRemision.lote_id,
        taller_id: dataRemision.taller_id,
        fecha_remision: fechaRemision,
        fecha_entrega_estimada: fechaEntregaEstimada,
        observaciones: dataRemision.observaciones
      });
      dataRemision.detalles.forEach(detalle => {
        // Convertir fecha_entrega_estimada del detalle al formato para input type="date"
        let fechaEntregaDetalle = detalle.fecha_entrega_estimada;
        if (fechaEntregaDetalle && typeof fechaEntregaDetalle === 'string') {
          fechaEntregaDetalle = fechaEntregaDetalle.split('T')[0];
        }
        this.agregarDetalle(
          detalle.talla_id,
          detalle.cantidad,
          detalle.confeccionista_nombre,
          detalle.tipo_prenda,
          fechaEntregaDetalle
        );
      });
    }
  }

  private isRemision(data: RemisionFormData | null): data is Remision {
    return !!data && (data as Remision).numero_remision !== undefined && (data as Remision).lote_id !== undefined;
  }

  get detalles(): FormArray {
    return this.form.get('detalles') as FormArray;
  }

  agregarDetalle(tallaId?: number, cantidad?: number, confeccionistaNombre?: string, tipoPrenda?: string, fechaEntrega?: string): void {
    const detalleForm = this.fb.group({
      talla_id: [tallaId || '', Validators.required],
      cantidad: [cantidad || 0, [Validators.required, Validators.min(1)]],
      confeccionista_nombre: [confeccionistaNombre || ''],
      tipo_prenda: [tipoPrenda || ''],
      fecha_entrega_estimada: [fechaEntrega || '']
    });
    this.detalles.push(detalleForm);
  }

  eliminarDetalle(index: number): void {
    this.detalles.removeAt(index);
  }

  guardar(): void {
    if (this.form.valid) {
      if (this.detalles.length === 0) {
        this.snackBar.open('Debe agregar al menos una talla', 'Cerrar', { duration: 3000 });
        return;
      }

      const formValue = this.form.value;
      const remisionData: RemisionCreate = {
        numero_remision: formValue.numero_remision,
        lote_id: formValue.lote_id,
        taller_id: formValue.taller_id,
        fecha_remision: formValue.fecha_remision ? new Date(formValue.fecha_remision).toISOString() : new Date().toISOString(),
        fecha_entrega_estimada: formValue.fecha_entrega_estimada ? new Date(formValue.fecha_entrega_estimada).toISOString() : undefined,
        observaciones: formValue.observaciones || '',
        detalles: formValue.detalles.map((d: any) => {
          let fechaEntrega: string | undefined = undefined;
          if (d.fecha_entrega_estimada) {
            // Si viene como string (type="date" formato YYYY-MM-DD), convertir a ISO
            if (typeof d.fecha_entrega_estimada === 'string') {
              fechaEntrega = new Date(d.fecha_entrega_estimada + 'T00:00:00').toISOString();
            } else {
              fechaEntrega = new Date(d.fecha_entrega_estimada).toISOString();
            }
          }
          return {
            talla_id: d.talla_id,
            cantidad: parseInt(d.cantidad, 10),
            confeccionista_nombre: d.confeccionista_nombre?.trim() || undefined,
            tipo_prenda: d.tipo_prenda?.trim() || undefined,
            fecha_entrega_estimada: fechaEntrega
          };
        })
      };

      if (this.isEdit && this.data) {
        this.tallerService.actualizarRemision((this.data as Remision).id, remisionData).subscribe({
          next: () => {
            this.snackBar.open('Remisión actualizada correctamente', 'Cerrar', { duration: 3000 });
            this.dialogRef.close(true);
          },
          error: (error) => {
            console.error('Error actualizando remisión:', error);
            const mensaje = error.error?.detail || error.message || 'Error al actualizar remisión';
            this.snackBar.open(mensaje, 'Cerrar', { duration: 5000 });
          }
        });
      } else {
        this.tallerService.crearRemision(remisionData).subscribe({
          next: () => {
            this.snackBar.open('Remisión creada correctamente', 'Cerrar', { duration: 3000 });
            this.dialogRef.close(true);
          },
          error: (error) => {
            console.error('Error creando remisión:', error);
            const mensaje = error.error?.detail || error.message || 'Error al crear remisión';
            this.snackBar.open(mensaje, 'Cerrar', { duration: 5000 });
          }
        });
      }
    } else {
      this.snackBar.open('Por favor complete todos los campos requeridos', 'Cerrar', { duration: 3000 });
    }
  }

  cancelar(): void {
    this.dialogRef.close();
  }
}
