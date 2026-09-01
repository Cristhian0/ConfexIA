/**
 * Componente de Insights de IA para el Dashboard
 * Muestra predicciones, anomalías y recomendaciones
 */

import { Component, OnInit, OnDestroy } from '@angular/core';
import { PrediccionesService, AnaliseDatos, InsightDashboard } from '../../../services/predicciones.service';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-ia-insights',
  templateUrl: './ia-insights.component.html',
  styleUrls: ['./ia-insights.component.scss']
})
export class IaInsightsComponent implements OnInit, OnDestroy {
  
  cargando = false;
  error: string | null = null;
  analisis: AnaliseDatos | null = null;
  insights: InsightDashboard[] = [];
  
  private destroy$ = new Subject<void>();

  constructor(private prediccionesService: PrediccionesService) {}

  ngOnInit(): void {
    this.cargarInsights();
    // Recargar cada 5 minutos
    setInterval(() => this.cargarInsights(), 5 * 60 * 1000);
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Carga los insights del backend
   */
  cargarInsights(): void {
    this.cargando = true;
    this.error = null;

    this.prediccionesService.obtenerInsights()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (datos: AnaliseDatos) => {
          this.analisis = datos;
          this.insights = datos.insights || [];
          this.cargando = false;
        },
        error: (err: any) => {
          this.error = 'Error cargando insights: ' + err.message;
          this.cargando = false;
          console.error('Error:', err);
        }
      });
  }

  /**
   * Obtiene el icono para el tipo de alerta
   */
  getIconoAlerta(tipo: string): string {
    const iconos: { [key: string]: string } = {
      'info': 'info_outline',
      'warning': 'warning_outline',
      'error': 'error_outline',
      'success': 'check_circle_outline'
    };
    return iconos[tipo] || 'info_outline';
  }

  /**
   * Obtiene el color para el tipo de alerta
   */
  getColorAlerta(tipo: string): string {
    const colores: { [key: string]: string } = {
      'info': 'info',
      'warning': 'warning',
      'error': 'error',
      'success': 'success'
    };
    return colores[tipo] || 'info';
  }

  /**
   * Formatea el valor principal según la unidad
   */
  formatearValor(valor: number, unidad: string): string {
    if (unidad.includes('%')) {
      return `${Math.round(valor)}%`;
    }
    if (unidad.includes('unidades')) {
      return `${Math.round(valor)} un.`;
    }
    if (unidad.includes('día')) {
      return `${Math.round(valor)}/día`;
    }
    return valor.toFixed(2);
  }
}
