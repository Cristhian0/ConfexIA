import { Component, OnInit } from '@angular/core';
import { FormArray, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { CorteService, OrdenCorte, OrdenCorteUpdateTizado, OrdenCorteUpdateCorte, OrdenCorteUpdateSobrantes } from '../../services/corte.service';
import { TizadoDialogComponent } from './tizado-dialog.component';
import { CorteDialogComponent } from './corte-dialog.component';
import { SobrantesDialogComponent } from './sobrantes-dialog.component';

export interface Merma {
  corte: string;
  tipo_corte: string;
  medida: string;
  peso: number;
}

@Component({
  selector: 'app-corte',
  templateUrl: './corte.component.html',
  styleUrls: ['./corte.component.scss']
})
export class CorteComponent implements OnInit {
  ordenes: OrdenCorte[] = [];
  displayedColumns = ['numero', 'prenda', 'estado', 'tallas', 'acciones'];
  loading = false;
  form: FormGroup;
  mermaForm: FormGroup;
  mermas: Merma[] = [];

  constructor(
    private corteService: CorteService,
    private fb: FormBuilder,
    private dialog: MatDialog
  ) {
    this.form = this.fb.group({
      tipo_prenda: ['', [Validators.required, Validators.maxLength(120)]],
      lineas: this.fb.array([this.nuevaLinea()])
    });

    this.mermaForm = this.fb.group({
      corte: ['', [Validators.required, Validators.maxLength(120)]],
      tipo_corte: ['', [Validators.required, Validators.maxLength(120)]],
      medida: ['', [Validators.required, Validators.maxLength(80)]],
      peso: [0, [Validators.required, Validators.min(0)]]
    });
  }

  get lineas(): FormArray {
    return this.form.get('lineas') as FormArray;
  }

  nuevaLinea(): FormGroup {
    return this.fb.group({
      talla_codigo: ['', Validators.required],
      cantidad: [0, [Validators.required, Validators.min(0)]]
    });
  }

  agregarLinea(): void {
    this.lineas.push(this.nuevaLinea());
  }

  quitarLinea(i: number): void {
    if (this.lineas.length > 1) {
      this.lineas.removeAt(i);
    }
  }

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.loading = true;
    this.corteService.listarOrdenes().subscribe({
      next: (data) => {
        this.ordenes = data;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  private limpiarLineas(lineas: Array<{ talla_codigo: string; cantidad: number }>): Array<{ talla_codigo: string; cantidad: number }> {
    return lineas
      .map((l) => ({
        talla_codigo: String(l.talla_codigo).trim(),
        cantidad: Number(l.cantidad)
      }))
      .filter((l) => l.talla_codigo.length > 0);
  }

  formatLineas(lineas: OrdenCorte['lineas']): string {
    return lineas.map((l) => `${l.talla_codigo}:${l.cantidad}`).join(', ');
  }

  guardarMerma(): void {
    if (this.mermaForm.invalid) {
      this.mermaForm.markAllAsTouched();
      return;
    }

    const value = this.mermaForm.value;
    this.mermas.push({
      corte: String(value.corte).trim(),
      tipo_corte: String(value.tipo_corte).trim(),
      medida: String(value.medida).trim(),
      peso: Number(value.peso)
    });

    this.mermaForm.reset({
      corte: '',
      tipo_corte: '',
      medida: '',
      peso: 0
    });
  }

  borrarMerma(index: number): void {
    this.mermas.splice(index, 1);
  }

  guardar(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const v = this.form.value;
    const lineas = this.limpiarLineas(v.lineas);
    if (!lineas.length) {
      alert('Es necesario ingresar al menos una talla con cantidad para crear la orden.');
      return;
    }

    this.corteService
      .crearOrden({
        tipo_prenda: String(v.tipo_prenda).trim(),
        lineas
      })
      .subscribe({
        next: () => {
          this.form.reset({ tipo_prenda: '', lineas: [] });
          this.lineas.clear();
          this.lineas.push(this.nuevaLinea());
          this.cargar();
        },
        error: (error) => {
          console.error('Error creando orden de corte:', error);
          alert('Error al crear la orden. Por favor revisa los datos e intenta de nuevo.');
        }
      });
  }

  // RF-05: Registrar tizado
  abrirTizadoDialog(orden: OrdenCorte): void {
    const dialogRef = this.dialog.open(TizadoDialogComponent, {
      width: '500px',
      data: { orden }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.actualizarOrdenEnLista(result);
        alert('Tizado registrado exitosamente');
      }
    });
  }

  // RF-06: Registrar corte
  abrirCorteDialog(orden: OrdenCorte): void {
    const dialogRef = this.dialog.open(CorteDialogComponent, {
      width: '500px',
      data: { orden }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.actualizarOrdenEnLista(result);
        alert('Corte registrado exitosamente');
      }
    });
  }

  // RF-07: Registrar sobrantes
  abrirSobrantesDialog(orden: OrdenCorte): void {
    const dialogRef = this.dialog.open(SobrantesDialogComponent, {
      width: '500px',
      data: { orden }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.actualizarOrdenEnLista(result);
        alert('Sobrantes registrados exitosamente');
      }
    });
  }

  private actualizarOrdenEnLista(ordenActualizada: OrdenCorte): void {
    const index = this.ordenes.findIndex(o => o.id === ordenActualizada.id);
    if (index !== -1) {
      this.ordenes[index] = ordenActualizada;
    }
  }
}
