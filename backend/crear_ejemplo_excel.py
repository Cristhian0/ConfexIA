"""
Script para crear un archivo Excel de ejemplo para importar lotes
"""
import pandas as pd
from datetime import datetime

# Crear datos de ejemplo para un lote con múltiples detalles
# Cada fila representa una combinación de Color + Talla + Cantidad

datos = [
    {
        'Mesa': 'Mesa 1',
        'Fecha Corte': '2026-01-15',
        'Referencia': 'Camiseta Básica',  # Puede ser código o nombre
        'Material': 'Algodón',  # Puede ser código o nombre
        'Color': 'Negro',  # Nombre del color
        'Talla': 'S',  # Código de la talla
        'Cantidad': 10,
        'Observaciones': 'Lote de prueba',
        'Prioridad': 0  # 0=normal, 1=alta, 2=urgente
    },
    {
        'Mesa': 'Mesa 1',
        'Fecha Corte': '2026-01-15',
        'Referencia': 'Camiseta Básica',
        'Material': 'Algodón',
        'Color': 'Negro',
        'Talla': 'M',
        'Cantidad': 15,
        'Observaciones': 'Lote de prueba',
        'Prioridad': 0
    },
    {
        'Mesa': 'Mesa 1',
        'Fecha Corte': '2026-01-15',
        'Referencia': 'Camiseta Básica',
        'Material': 'Algodón',
        'Color': 'Negro',
        'Talla': 'L',
        'Cantidad': 12,
        'Observaciones': 'Lote de prueba',
        'Prioridad': 0
    },
    {
        'Mesa': 'Mesa 1',
        'Fecha Corte': '2026-01-15',
        'Referencia': 'Camiseta Básica',
        'Material': 'Algodón',
        'Color': 'Blanco',
        'Talla': 'S',
        'Cantidad': 8,
        'Observaciones': 'Lote de prueba',
        'Prioridad': 0
    },
    {
        'Mesa': 'Mesa 1',
        'Fecha Corte': '2026-01-15',
        'Referencia': 'Camiseta Básica',
        'Material': 'Algodón',
        'Color': 'Blanco',
        'Talla': 'M',
        'Cantidad': 10,
        'Observaciones': 'Lote de prueba',
        'Prioridad': 0
    },
    {
        'Mesa': 'Mesa 1',
        'Fecha Corte': '2026-01-15',
        'Referencia': 'Camiseta Básica',
        'Material': 'Algodón',
        'Color': 'Blanco',
        'Talla': 'L',
        'Cantidad': 5,
        'Observaciones': 'Lote de prueba',
        'Prioridad': 0
    }
]

# Crear DataFrame
df = pd.DataFrame(datos)

# Guardar como Excel
archivo_excel = 'ejemplo_importacion_lotes.xlsx'
df.to_excel(archivo_excel, index=False, engine='openpyxl')

print(f"✓ Archivo Excel creado: {archivo_excel}")
print(f"\nResumen del archivo:")
print(f"- Total de filas (detalles): {len(df)}")
print(f"- Mesa: {df['Mesa'].iloc[0]}")
print(f"- Fecha Corte: {df['Fecha Corte'].iloc[0]}")
print(f"- Referencia: {df['Referencia'].iloc[0]}")
print(f"- Material: {df['Material'].iloc[0]}")
print(f"- Colores: {', '.join(df['Color'].unique())}")
print(f"- Tallas: {', '.join(df['Talla'].unique())}")
print(f"- Cantidad total: {df['Cantidad'].sum()} unidades")
print(f"\nColumnas del archivo:")
for col in df.columns:
    print(f"  - {col}")

print(f"\n📝 NOTA: Asegúrate de que los valores de 'Referencia', 'Material' y 'Talla'")
print(f"   existan en el catálogo de la base de datos antes de importar.")

