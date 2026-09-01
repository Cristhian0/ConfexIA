import { Component, OnInit } from '@angular/core';
import { FinancieroService } from '../../services/financiero.service';
import { Indicadores, ProduccionDiaLinea } from '../../models/financiero.model';

@Component({
  selector: 'app-financiero',
  templateUrl: './financiero.component.html',
  styleUrls: ['./financiero.component.scss']
})
export class FinancieroComponent implements OnInit {
  indicadores: Indicadores | null = null;
  produccionDiaLinea: ProduccionDiaLinea[] = [];
  loading = true;
  error = '';

  constructor(private financieroService: FinancieroService) { }

  ngOnInit(): void {
    this.cargarDatos();
  }

  cargarDatos(): void {
    this.loading = true;
    this.error = '';

    this.financieroService.obtenerIndicadores().subscribe({
      next: (data) => {
        this.indicadores = data;
        this.loading = false;
      },
      error: (e) => {
        console.error('Error cargando indicadores:', e);
        this.error = 'Error cargando indicadores';
        this.loading = false;
      }
    });

    this.financieroService.obtenerProduccionDiaLinea().subscribe({
      next: (data) => {
        this.produccionDiaLinea = data;
      },
      error: (e) => {
        console.error('Error cargando producción por día/línea:', e);
      }
    });
  }
}
