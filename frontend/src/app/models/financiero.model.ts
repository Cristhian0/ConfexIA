export interface CostoPrenda {
  noc_id?: number;
  lote_id: number;
  total_prendas: number;
  costo_tela: number;
  costo_mano_obra: number;
  costo_insumos: number;
  costo_otros: number;
  costo_total: number;
  costo_unitario: number;
}

export interface RentabilidadLote {
  lote_id: number;
  total_prendas: number;
  anticipo_total: number;
  costo_total: number;
  rentabilidad: number;
  rentabilidad_pct?: number;
  costo_unitario_promedio: number;
}

export interface ProduccionDiaLinea {
  fecha: string;
  linea_produccion?: string;
  cantidad_producida: number;
  cantidad_rechazada: number;
  eficiencia_hph: number;
}

export interface EficienciaOperario {
  operario: string;
  produccion_total: number;
  horas_trabajadas: number;
  piezas_por_hora: number;
}

export interface Indicadores {
  desperdicio_tela_pct: number;
  defectos_pct: number;
  costo_unitario_promedio: number;
  eficiencia_operarios: EficienciaOperario[];
}
