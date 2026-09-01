"""
Script para ejecutar migraciones manualmente
Ejecutar: python migrate.py
"""
from app.db.migrations import ejecutar_migraciones

if __name__ == "__main__":
    print("Ejecutando migraciones de base de datos...")
    ejecutar_migraciones()
    print("\n¡Migraciones completadas!")

