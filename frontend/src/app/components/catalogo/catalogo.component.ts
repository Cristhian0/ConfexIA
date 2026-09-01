import { Component } from '@angular/core';

@Component({
  selector: 'app-catalogo',
  templateUrl: './catalogo.component.html',
  styleUrls: ['./catalogo.component.scss']
})
export class CatalogoComponent {
  selectedTabIndex = 0;

  onTabChange(index: number): void {
    this.selectedTabIndex = index;
  }
}

