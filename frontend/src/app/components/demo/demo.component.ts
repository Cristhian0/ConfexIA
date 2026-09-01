import { Component } from '@angular/core';

@Component({
  selector: 'app-demo',
  templateUrl: './demo.component.html',
  styleUrls: ['./demo.component.scss']
})
export class DemoComponent {
  constructor() {}

  viewDashboard() {
    // placeholder: expand later to navigate or open modal
    console.log('View dashboard (demo)');
  }

  viewModules() {
    console.log('View modules (demo)');
  }
}
