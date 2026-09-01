import { Component, OnInit, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { DashboardService, Estadisticas } from '../../services/dashboard.service';
import { Chart, registerables } from 'chart.js';

interface ProcessStep {
  label: string;
  icon: string;
  status: string;
}

interface InventarioItem {
  producto: string;
  disponible: number;
  unidad: string;
}

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit, AfterViewInit {
  @ViewChild('processChart') processChart?: ElementRef<HTMLCanvasElement>;
  @ViewChild('productionChart') productionChart?: ElementRef<HTMLCanvasElement>;

  processChartInstance?: Chart;
  productionChartInstance?: Chart;

  estadisticas: Estadisticas = {
    lotes_por_estado: {},
    prendas: {
      total: 0,
      en_corte: 0,
      en_taller: 0,
      confeccionadas: 0,
      entregadas: 0
    },
    talleres_activos: 0,
    remisiones_pendientes: 0,
    fallas_pendientes: 0,
    pedidos_especiales: 0
  };
  loading = false;

  processSteps: ProcessStep[] = [
    { label: 'Materia Prima', icon: 'shopping_cart', status: 'Ingresada' },
    { label: 'Corte y Tirado', icon: 'content_cut', status: 'En Proceso' },
    { label: 'Taller y Remisión', icon: 'local_shipping', status: 'Asignado' },
    { label: 'Creación de Lote', icon: 'precision_manufacturing', status: 'Creado' },
    { label: 'Control de Calidad', icon: 'fact_check', status: 'En Proceso' },
    { label: 'Producto Terminado', icon: 'done_all', status: 'Registrado' },
    { label: 'Inventario & Remisiones', icon: 'inventory_2', status: 'Disponible' },
    { label: 'Colillas', icon: 'description', status: 'Generadas' },
    { label: 'Revisión y Firma', icon: 'done', status: 'Aprobado' },
    { label: 'Descarga PDF', icon: 'download', status: 'Disponible' }
  ];

  inventarioBodega: InventarioItem[] = [
    { producto: 'Tela Algodón Azul', disponible: 320.50, unidad: 'm' },
    { producto: 'Tela Poliéster Negro', disponible: 215.30, unidad: 'm' },
    { producto: 'Tela Dril Beige', disponible: 180.75, unidad: 'm' },
    { producto: 'Hilo Blanco', disponible: 45.00, unidad: 'und' },
    { producto: 'Etiqueta Talla M', disponible: 2.350, unidad: 'und' }
  ];

  constructor(private dashboardService: DashboardService) {
    Chart.register(...registerables);
  }

  ngOnInit(): void {
    this.cargarDatos();
  }

  ngAfterViewInit(): void {
    setTimeout(() => {
      if (this.processChart && this.productionChart) {
        this.crearGraficos();
      }
    }, 500);
  }

  cargarDatos(): void {
    this.loading = true;
    this.dashboardService.obtenerEstadisticas().subscribe({
      next: (data) => {
        this.estadisticas = data || this.estadisticas;
        this.loading = false;
        setTimeout(() => this.crearGraficos(), 500);
      },
      error: (error) => {
        console.error('Error cargando estadísticas:', error);
        this.estadisticas = {
          lotes_por_estado: {},
          prendas: {
            total: 0,
            en_corte: 0,
            en_taller: 0,
            confeccionadas: 0,
            entregadas: 0
          },
          talleres_activos: 0,
          remisiones_pendientes: 0,
          fallas_pendientes: 0,
          pedidos_especiales: 0
        };
        this.loading = false;
        setTimeout(() => this.crearGraficos(), 500);
      }
    });
  }

  crearGraficos(): void {
    this.crearGraficoEstadoProceso();
    this.crearGraficoProduccionEstados();
  }

  private destruirGrafico(chartInstance?: Chart): void {
    if (chartInstance) {
      chartInstance.destroy();
    }
  }

  crearGraficoEstadoProceso(): void {
    if (!this.processChart?.nativeElement) return;

    const existingChart = this.processChartInstance;
    this.destruirGrafico(existingChart);

    const ctx = this.processChart.nativeElement.getContext('2d');
    if (!ctx) return;

    this.processChartInstance = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: [
          'Materia Prima',
          'Corte y Tirado',
          'Taller',
          'Control de Calidad',
          'Producto Terminado',
          'Inventario',
          'Colillas',
          'Revisión',
          'Descarga'
        ],
        datasets: [{
          data: [0, 0, 0, 0, 0, 0, 0, 0, 0],
          backgroundColor: [
            '#1976d2',
            '#ff6f00',
            '#d32f2f',
            '#7b1fa2',
            '#0097a7',
            '#00796b',
            '#f57c00',
            '#388e3c',
            '#c62828'
          ],
          borderColor: '#ffffff',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            position: 'right'
          }
        }
      }
    });
  }

  crearGraficoProduccionEstados(): void {
    if (!this.productionChart?.nativeElement) return;

    const existingChart = this.productionChartInstance;
    this.destruirGrafico(existingChart);

    const ctx = this.productionChart.nativeElement.getContext('2d');
    if (!ctx) return;

    this.productionChartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['En Corte', 'En Taller', 'En Calidad', 'Completados', 'Cancelados'],
        datasets: [{
          label: 'Lotes',
          data: [0, 0, 0, 0, 0],
          backgroundColor: [
            '#ff6f00',
            '#ffa726',
            '#ffb74d',
            '#66bb6a',
            '#ef5350'
          ],
          borderRadius: 4,
          borderSkipped: false
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        indexAxis: 'x',
        plugins: {
          legend: {
            display: true
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  }
}
