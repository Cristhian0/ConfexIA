import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'colorCode'
})
export class ColorCodePipe implements PipeTransform {
  // Mapeo de colores por ID a código hexadecimal
  private colorMap: { [key: number]: string } = {
    1: '#FF6B6B',  // Rojo
    2: '#4ECDC4',  // Turquesa
    3: '#45B7D1',  // Azul
    4: '#FFA07A',  // Salmón
    5: '#98D8C8',  // Menta
    6: '#F7DC6F',  // Amarillo
    7: '#BB8FCE',  // Púrpura
    8: '#85C1E2',  // Celeste
    9: '#F8B195',  // Naranja
    10: '#C7CEEA', // Lavanda
    11: '#FFB6C1', // Rosa
    12: '#90EE90', // Verde claro
    13: '#DEB887', // Marrón tan
    14: '#D3D3D3', // Gris claro
    15: '#2F4F4F'  // Gris oscuro
  };

  transform(colorId: number | string): string {
    const id = typeof colorId === 'string' ? parseInt(colorId, 10) : colorId;
    
    // Retornar el color del mapa o un color por defecto
    return this.colorMap[id] || '#CCCCCC';
  }
}
