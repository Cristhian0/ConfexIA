"""
Script para recrear la base de datos desde cero
Úsalo si tienes problemas con columnas legacy como color_id en lotes
"""
import os
from app.db.database import engine, Base
from app.core.config import settings

def recrear_base_datos():
    """Elimina y recrea la base de datos desde cero"""
    # Obtener la ruta de la base de datos
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
        if os.path.exists(db_path):
            print(f"Eliminando base de datos existente: {db_path}")
            os.remove(db_path)
            print("✓ Base de datos eliminada")
        else:
            print(f"La base de datos no existe en: {db_path}")
    
    # Crear todas las tablas
    print("Creando tablas...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tablas creadas exitosamente")
    
    print("\n✓ Base de datos recreada exitosamente")
    print("Ahora puedes reiniciar el servidor y comenzar a usar la aplicación")

if __name__ == "__main__":
    confirmacion = input("¿Estás seguro de que quieres eliminar y recrear la base de datos? (s/n): ")
    if confirmacion.lower() == 's':
        recrear_base_datos()
    else:
        print("Operación cancelada")

