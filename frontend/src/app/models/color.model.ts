export interface Color {
  id: number;
  codigo: string;
  nombre: string;
  color_hex?: string;
  activo: boolean;
  created_at: string;
  updated_at?: string;
}

export interface ColorCreate {
  codigo: string;
  nombre: string;
  color_hex?: string;
  activo?: boolean;
}

export interface ColorUpdate {
  codigo?: string;
  nombre?: string;
  color_hex?: string;
  activo?: boolean;
}

