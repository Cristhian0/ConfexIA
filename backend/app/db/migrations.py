"""
Script de migración para agregar nuevas columnas a las tablas existentes
"""
from sqlalchemy import text
from app.db.database import engine

def ejecutar_migraciones():
    """Ejecuta las migraciones necesarias para actualizar el esquema de la base de datos"""
    with engine.connect() as conn:
        try:
            # Verificar si la columna 'mesa' existe en la tabla 'lotes'
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM pragma_table_info('lotes') 
                WHERE name='mesa'
            """))
            mesa_exists = result.fetchone()[0] > 0
            
            if not mesa_exists:
                print("Agregando columna 'mesa' a la tabla 'lotes'...")
                conn.execute(text("ALTER TABLE lotes ADD COLUMN mesa VARCHAR(50)"))
                conn.commit()
                print("✓ Columna 'mesa' agregada")
            
            # Verificar si la columna 'cantidad_total_programada' existe
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM pragma_table_info('lotes') 
                WHERE name='cantidad_total_programada'
            """))
            cantidad_exists = result.fetchone()[0] > 0
            
            if not cantidad_exists:
                print("Agregando columna 'cantidad_total_programada' a la tabla 'lotes'...")
                conn.execute(text("ALTER TABLE lotes ADD COLUMN cantidad_total_programada INTEGER DEFAULT 0"))
                conn.commit()
                print("✓ Columna 'cantidad_total_programada' agregada")

            # Verificar y agregar columnas nuevas para remisión, confeccionista, entrega y despacha
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM pragma_table_info('lotes') 
                WHERE name='remision_numero'
            """))
            remision_exists = result.fetchone()[0] > 0
            if not remision_exists:
                print("Agregando columna 'remision_numero' a la tabla 'lotes'...")
                conn.execute(text("ALTER TABLE lotes ADD COLUMN remision_numero VARCHAR(200)"))
                conn.commit()
                print("✓ Columna 'remision_numero' agregada")

            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM pragma_table_info('lotes') 
                WHERE name='confeccionista_nombre'
            """))
            confecc_exists = result.fetchone()[0] > 0
            if not confecc_exists:
                print("Agregando columna 'confeccionista_nombre' a la tabla 'lotes'...")
                conn.execute(text("ALTER TABLE lotes ADD COLUMN confeccionista_nombre VARCHAR(200)"))
                conn.commit()
                print("✓ Columna 'confeccionista_nombre' agregada")

            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM pragma_table_info('lotes') 
                WHERE name='fecha_entrega'
            """))
            fecha_ent_exists = result.fetchone()[0] > 0
            if not fecha_ent_exists:
                print("Agregando columna 'fecha_entrega' a la tabla 'lotes'...")
                conn.execute(text("ALTER TABLE lotes ADD COLUMN fecha_entrega DATETIME"))
                conn.commit()
                print("✓ Columna 'fecha_entrega' agregada")

            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM pragma_table_info('lotes') 
                WHERE name='fecha_entrega_estimada'
            """))
            fecha_ent_est_exists = result.fetchone()[0] > 0
            if not fecha_ent_est_exists:
                print("Agregando columna 'fecha_entrega_estimada' a la tabla 'lotes'...")
                conn.execute(text("ALTER TABLE lotes ADD COLUMN fecha_entrega_estimada DATETIME"))
                conn.commit()
                print("✓ Columna 'fecha_entrega_estimada' agregada")

            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM pragma_table_info('lotes') 
                WHERE name='despacha'
            """))
            despacha_exists = result.fetchone()[0] > 0
            if not despacha_exists:
                print("Agregando columna 'despacha' a la tabla 'lotes'...")
                conn.execute(text("ALTER TABLE lotes ADD COLUMN despacha INTEGER DEFAULT 0"))
                conn.commit()
                print("✓ Columna 'despacha' agregada")
            
            # Verificar si la columna 'color_hex' existe en 'colores'
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM pragma_table_info('colores') 
                WHERE name='color_hex'
            """))
            color_hex_exists = result.fetchone()[0] > 0
            
            if not color_hex_exists:
                print("Agregando columna 'color_hex' a la tabla 'colores'...")
                conn.execute(text("ALTER TABLE colores ADD COLUMN color_hex VARCHAR(7)"))
                conn.commit()
                print("✓ Columna 'color_hex' agregada a 'colores'")

            # Verificar si la columna 'firma_base64' existe en 'colillas'
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM pragma_table_info('colillas')
                WHERE name='firma_base64'
            """))
            firma_base64_exists = result.fetchone()[0] > 0

            if not firma_base64_exists:
                print("Agregando columna 'firma_base64' a la tabla 'colillas'...")
                conn.execute(text("ALTER TABLE colillas ADD COLUMN firma_base64 TEXT"))
                conn.commit()
                print("✓ Columna 'firma_base64' agregada a 'colillas'")

            # Verificar si la columna 'color_nombre' existe en 'lote_detalles'
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM pragma_table_info('lote_detalles') 
                WHERE name='color_nombre'
            """))
            color_nombre_exists = result.fetchone()[0] > 0
            
            if not color_nombre_exists:
                print("Agregando columna 'color_nombre' a la tabla 'lote_detalles'...")
                conn.execute(text("ALTER TABLE lote_detalles ADD COLUMN color_nombre VARCHAR(100)"))
                conn.commit()
                print("✓ Columna 'color_nombre' agregada a 'lote_detalles'")
            
            # Si existe color_id, migrar los nombres de color
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM pragma_table_info('lote_detalles') 
                WHERE name='color_id'
            """))
            color_id_exists = result.fetchone()[0] > 0
            
            if color_id_exists:
                print("Migrando color_id a color_nombre...")
                try:
                    # Actualizar color_nombre desde la tabla colores usando color_id
                    conn.execute(text("""
                        UPDATE lote_detalles 
                        SET color_nombre = (
                            SELECT nombre 
                            FROM colores 
                            WHERE colores.id = lote_detalles.color_id
                        )
                        WHERE color_id IS NOT NULL AND (color_nombre IS NULL OR color_nombre = '')
                    """))
                    conn.commit()
                    print("✓ Colores migrados de ID a nombre")
                    
                    # Actualizar registros que aún tienen NULL (usar un valor por defecto)
                    result = conn.execute(text("""
                        SELECT COUNT(*) as count 
                        FROM lote_detalles 
                        WHERE color_nombre IS NULL
                    """))
                    detalles_sin_color = result.fetchone()[0]
                    
                    if detalles_sin_color > 0:
                        print(f"Encontrados {detalles_sin_color} detalles sin color_nombre")
                        # Intentar obtener un color por defecto
                        result = conn.execute(text("SELECT nombre FROM colores LIMIT 1"))
                        color_default = result.fetchone()
                        if color_default:
                            color_nombre_default = color_default[0]
                            print(f"Actualizando detalles sin color con '{color_nombre_default}'...")
                            conn.execute(text(f"""
                                UPDATE lote_detalles 
                                SET color_nombre = '{color_nombre_default}'
                                WHERE color_nombre IS NULL
                            """))
                            conn.commit()
                            print("✓ Detalles sin color actualizados")
                        else:
                            print("⚠ No hay colores en el catálogo para usar como valor por defecto")
                except Exception as e:
                    print(f"⚠ Error migrando colores: {e}")
            
            # Verificar y agregar columnas nuevas en remision_detalles para confeccionista
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM pragma_table_info('remision_detalles')
                WHERE name='confeccionista_nombre'
            """))
            confeccionista_exists = result.fetchone()[0] > 0

            if not confeccionista_exists:
                print("Agregando columna 'confeccionista_nombre' a 'remision_detalles'...")
                conn.execute(text("ALTER TABLE remision_detalles ADD COLUMN confeccionista_nombre VARCHAR(200)"))
                conn.commit()
                print("✓ Columna 'confeccionista_nombre' agregada")

            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM pragma_table_info('remision_detalles')
                WHERE name='tipo_prenda'
            """))
            tipo_prenda_exists = result.fetchone()[0] > 0

            if not tipo_prenda_exists:
                print("Agregando columna 'tipo_prenda' a 'remision_detalles'...")
                conn.execute(text("ALTER TABLE remision_detalles ADD COLUMN tipo_prenda VARCHAR(200)"))
                conn.commit()
                print("✓ Columna 'tipo_prenda' agregada")

            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM pragma_table_info('remision_detalles')
                WHERE name='fecha_entrega_estimada'
            """))
            fecha_entrega_exists = result.fetchone()[0] > 0

            if not fecha_entrega_exists:
                print("Agregando columna 'fecha_entrega_estimada' a 'remision_detalles'...")
                conn.execute(text("ALTER TABLE remision_detalles ADD COLUMN fecha_entrega_estimada DATETIME"))
                conn.commit()
                print("✓ Columna 'fecha_entrega_estimada' agregada")

            # Verificar si la columna 'revisado_por' existe en 'remisiones'
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM pragma_table_info('remisiones') 
                WHERE name='revisado_por'
            """))
            revisado_por_exists = result.fetchone()[0] > 0
            
            if not revisado_por_exists:
                print("Agregando columna 'revisado_por' a la tabla 'remisiones'...")
                conn.execute(text("ALTER TABLE remisiones ADD COLUMN revisado_por VARCHAR(200)"))
                conn.commit()
                print("✓ Columna 'revisado_por' agregada")
            
            # Verificar si existe la columna color_id en lotes (legacy)
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM pragma_table_info('lotes') 
                WHERE name='color_id'
            """))
            color_id_lote_exists = result.fetchone()[0] > 0
            
            if color_id_lote_exists:
                print("⚠ La columna 'color_id' existe en 'lotes' (legacy)")
                # Hacer la columna nullable para que no cause errores
                try:
                    # SQLite no soporta ALTER COLUMN directamente, pero podemos intentar recrear la tabla
                    # Por ahora, simplemente haremos que sea nullable usando una actualización
                    # Nota: SQLite tiene limitaciones, así que solo podemos hacer que acepte NULL
                    print("  Intentando hacer 'color_id' nullable...")
                    # En SQLite, no podemos cambiar NOT NULL directamente sin recrear la tabla
                    # Por ahora, solo informamos que existe
                    print("  ⚠ Nota: La columna 'color_id' en 'lotes' puede causar problemas.")
                    print("  Considera recrear la base de datos o usar una migración manual.")
                except Exception as e:
                    print(f"  ⚠ No se pudo modificar 'color_id': {e}")
            
            # Verificar y crear tablas de control de calidad
            # Nota: En SQLite, las tablas se crean automáticamente con SQLAlchemy
            # pero podemos verificar que existan las nuevas columnas si es necesario
            # Agregar nuevas columnas solicitadas en 'controles_calidad'
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM pragma_table_info('controles_calidad')
                WHERE name='fecha_recepcion'
            """))
            fecha_recepcion_exists = result.fetchone()[0] > 0

            if not fecha_recepcion_exists:
                print("Agregando columna 'fecha_recepcion' a 'controles_calidad'...")
                conn.execute(text("ALTER TABLE controles_calidad ADD COLUMN fecha_recepcion DATETIME"))
                conn.commit()
                print("✓ Columna 'fecha_recepcion' agregada")

            # revisado_por
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM pragma_table_info('controles_calidad')
                WHERE name='revisado_por'
            """))
            revisado_por_exists = result.fetchone()[0] > 0

            if not revisado_por_exists:
                print("Agregando columna 'revisado_por' a 'controles_calidad'...")
                conn.execute(text("ALTER TABLE controles_calidad ADD COLUMN revisado_por VARCHAR(200)"))
                conn.commit()
                print("✓ Columna 'revisado_por' agregada")

            # Cantidades y flags
            cols_to_add = [
                ("cantidad_parcial", "INTEGER DEFAULT 0"),
                ("cantidad_arreglos", "INTEGER DEFAULT 0"),
                ("tiene_imperfecciones", "INTEGER DEFAULT 0"),
                ("cantidad_pendiente", "INTEGER DEFAULT 0"),
                ("requiere_compras", "INTEGER DEFAULT 0"),
                ("fecha_entrega_total", "DATETIME"),
                ("dias_mora", "INTEGER DEFAULT 0"),
                ("estado_pago", "VARCHAR(50)")
            ]

            for col_name, col_def in cols_to_add:
                result = conn.execute(text(f"""
                    SELECT COUNT(*) as count
                    FROM pragma_table_info('controles_calidad')
                    WHERE name='{col_name}'
                """))
                exists = result.fetchone()[0] > 0
                if not exists:
                    print(f"Agregando columna '{col_name}' a 'controles_calidad'...")
                    conn.execute(text(f"ALTER TABLE controles_calidad ADD COLUMN {col_name} {col_def}"))
                    conn.commit()
                    print(f"✓ Columna '{col_name}' agregada")
            
            # FK opcional lote -> orden de corte (RF-09 trazabilidad)
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM pragma_table_info('lotes')
                WHERE name='orden_corte_id'
            """))
            orden_corte_fk_exists = result.fetchone()[0] > 0

            if not orden_corte_fk_exists:
                print("Agregando columna 'orden_corte_id' a 'lotes'...")
                conn.execute(text("ALTER TABLE lotes ADD COLUMN orden_corte_id INTEGER"))
                conn.commit()
                print("✓ Columna 'orden_corte_id' agregada (relación con ordenes_corte)")
            
            # RF-03: Verificar si la columna 'cantidad_reservada' existe en 'rollo_stocks'
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM pragma_table_info('rollo_stocks') 
                WHERE name='cantidad_reservada'
            """))
            cantidad_reservada_exists = result.fetchone()[0] > 0
            
            if not cantidad_reservada_exists:
                print("Agregando columna 'cantidad_reservada' a la tabla 'rollo_stocks'...")
                conn.execute(text("ALTER TABLE rollo_stocks ADD COLUMN cantidad_reservada DECIMAL(12,2) DEFAULT 0"))
                conn.commit()
                print("✓ Columna 'cantidad_reservada' agregada")

            print("\n✓ Migraciones completadas exitosamente")
            
        except Exception as e:
            print(f"Error ejecutando migraciones: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    ejecutar_migraciones()

