import { Component } from '@angular/core';

@Component({
  selector: 'app-landing-chart',
  templateUrl: './landing-chart.component.html',
  styleUrls: ['./landing-chart.component.scss']
})
export class LandingChartComponent {
  // Static sample data (meses, valores reales y predicción IA)
  data = {
    months: ['Ene','Feb','Mar','Abr','May','Jun'],
    real: [120, 150, 130, 170, 160, 180],
    pred: [110, 140, 135, 165, 170, 190]
  };
}
