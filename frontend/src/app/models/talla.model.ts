export interface Talla {
  id: number;
  codigo: string;
  nombre: string;
  activo: boolean;
  created_at: string;
  updated_at?: string;
}

export interface TallaCreate {
  codigo: string;
  nombre: string;
  activo?: boolean;
}

export interface TallaUpdate {
  codigo?: string;
  nombre?: string;
  activo?: boolean;
}

