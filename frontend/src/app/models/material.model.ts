export interface Material {
  id: number;
  codigo: string;
  nombre: string;
  descripcion?: string;
  activo: boolean;
  created_at: string;
  updated_at?: string;
}

export interface MaterialCreate {
  codigo: string;
  nombre: string;
  descripcion?: string;
  activo?: boolean;
}

export interface MaterialUpdate {
  codigo?: string;
  nombre?: string;
  descripcion?: string;
  activo?: boolean;
}

