import { Component, EventEmitter, Output } from '@angular/core';

@Component({
  selector: 'app-assistant',
  templateUrl: './assistant.component.html',
  styleUrls: ['./assistant.component.scss']
})
export class AssistantComponent {
  @Output() ask = new EventEmitter<string>();

  examples: string[] = [
    '¿Cuál es el taller más productivo?',
    '¿Qué lotes están retrasados?',
    '¿Qué referencia genera mayor rentabilidad?',
    '¿Qué inventario está próximo a agotarse?'
  ];

  askExample(q: string){
    this.ask.emit(q);
  }

}
