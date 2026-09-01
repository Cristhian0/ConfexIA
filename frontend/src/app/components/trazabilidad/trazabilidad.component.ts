import { Component, OnInit, Input } from '@angular/core';
import { CorteService } from '../../services/corte.service';
import { LoteService } from '../../services/lote.service';
import { InventarioTelaService } from '../../services/inventario-tela.service';
import { OrdenCorteBasica } from '../../models/lote.model';

@Component({
  selector: 'app-trazabilidad',
  template: `
    <div class="trazabilidad-container" *ngIf="ordenCorte">
      <h3>Trazabilidad: Tela → Corte → Lote</h3>

      <div class="trazabilidad-chain">
        <!-- Tela -->
        <div class="chain-item tela">
          <div class="item-header">
            <mat-icon>tune</mat-icon>
            <span>Tela</span>
          </div>
          <div class="item-content">
            <p><strong>Material:</strong> {{ ordenCorte.material_nombre || 'No especificado' }}</p>
            <p><strong>Color:</strong> {{ ordenCorte.color_nombre || 'No especificado' }}</p>
            <p><strong>Metros utilizados:</strong> {{ ordenCorte.metros_tizado || 0 }}m</p>
          </div>
        </div>

        <mat-icon class="arrow">arrow_forward</mat-icon>

        <!-- Corte -->
        <div class="chain-item corte">
          <div class="item-header">
            <mat-icon>content_cut</mat-icon>
            <span>Corte</span>
          </div>
          <div class="item-content">
            <p><strong>Orden:</strong> {{ ordenCorte.numero_orden }}</p>
            <p><strong>Tipo de prenda:</strong> {{ ordenCorte.tipo_prenda }}</p>
            <p><strong>Estado:</strong> {{ ordenCorte.estado }}</p>
            <p><strong>Piezas cortadas:</strong> {{ ordenCorte.piezas_cortadas || 0 }}</p>
            <p><strong>Rendimiento:</strong> {{ ordenCorte.rendimiento_pct || 0 }}%</p>
          </div>
        </div>

        <mat-icon class="arrow">arrow_forward</mat-icon>

        <!-- Lote -->
        <div class="chain-item lote">
          <div class="item-header">
            <mat-icon>inventory</mat-icon>
            <span>Lote</span>
          </div>
          <div class="item-content">
            <p><strong>Número:</strong> {{ lote?.numero_lote || 'No asociado' }}</p>
            <p><strong>Referencia:</strong> {{ lote?.referencia_nombre || 'No especificada' }}</p>
            <p><strong>Estado:</strong> {{ lote?.estado || 'No disponible' }}</p>
            <p><strong>Cantidad programada:</strong> {{ lote?.cantidad_total_programada || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="trazabilidad-details" *ngIf="ordenCorte.lineas && ordenCorte.lineas.length > 0">
        <h4>Detalles de producción</h4>
        <table mat-table [dataSource]="ordenCorte.lineas" class="mat-elevation-z2">
          <ng-container matColumnDef="talla">
            <th mat-header-cell *matHeaderCellDef>Talla</th>
            <td mat-cell *matCellDef="let linea">{{ linea.talla_codigo }}</td>
          </ng-container>

          <ng-container matColumnDef="cantidad">
            <th mat-header-cell *matHeaderCellDef>Cantidad</th>
            <td mat-cell *matCellDef="let linea">{{ linea.cantidad }}</td>
          </ng-container>

          <tr mat-header-row *matHeaderRowDef="['talla', 'cantidad']"></tr>
          <tr mat-row *matRowDef="let row; columns: ['talla', 'cantidad'];"></tr>
        </table>
      </div>
    </div>
  `,
  styles: [`
    .trazabilidad-container {
      margin: 20px 0;
      padding: 20px;
      background: #f8f9fa;
      border-radius: 8px;
    }

    h3 {
      color: #1f2937;
      margin-bottom: 20px;
      text-align: center;
    }

    .trazabilidad-chain {
      display: flex;
      align-items: center;
      justify-content: center;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 30px;
    }

    .chain-item {
      background: white;
      border-radius: 8px;
      padding: 15px;
      min-width: 200px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .item-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 10px;
      font-weight: 500;
      color: #374151;
    }

    .item-content p {
      margin: 5px 0;
      font-size: 14px;
      color: #6b7280;
    }

    .tela .item-header { color: #059669; }
    .corte .item-header { color: #dc2626; }
    .lote .item-header { color: #7c3aed; }

    .arrow {
      color: #9ca3af;
      font-size: 24px;
    }

    .trazabilidad-details {
      margin-top: 20px;
    }

    h4 {
      color: #1f2937;
      margin-bottom: 15px;
    }

    table {
      width: 100%;
      max-width: 400px;
      margin: 0 auto;
    }

    @media (max-width: 768px) {
      .trazabilidad-chain {
        flex-direction: column;
      }

      .arrow {
        transform: rotate(90deg);
      }
    }
  `]
})
export class TrazabilidadComponent implements OnInit {
  @Input() ordenCorteId: number | null = null;
  @Input() loteId: number | null = null;

  ordenCorte: any = null;
  lote: any = null;

  constructor(
    private corteService: CorteService,
    private loteService: LoteService,
    private inventarioService: InventarioTelaService
  ) {}

  ngOnInit(): void {
    this.cargarTrazabilidad();
  }

  ngOnChanges(): void {
    this.cargarTrazabilidad();
  }

  cargarTrazabilidad(): void {
    if (this.ordenCorteId) {
      this.corteService.obtenerOrden(this.ordenCorteId).subscribe({
        next: (orden) => {
          this.ordenCorte = orden;
          // No cargar lote automáticamente desde orden, usar el loteId si está disponible
        },
        error: (error) => {
          console.error('Error cargando orden de corte:', error);
        }
      });
    }

    if (this.loteId) {
      this.loteService.obtener(this.loteId).subscribe({
        next: (lote) => {
          this.lote = lote;
          // Si el lote tiene una orden de corte asociada, cargarla
          if (lote.orden_corte_id && !this.ordenCorte) {
            this.corteService.obtenerOrden(lote.orden_corte_id).subscribe({
              next: (orden) => {
                this.ordenCorte = orden;
              },
              error: (error) => {
                console.error('Error cargando orden de corte:', error);
              }
            });
          }
        },
        error: (error) => {
          console.error('Error cargando lote:', error);
        }
      });
    }
  }
}