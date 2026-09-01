from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
import io
import logging
import traceback
import re
from app.db.database import get_db
from app.models import Lote, LoteDetalle, Referencia, Color, Material, Talla
from app.schemas.lote import LoteCreate, LoteDetalleCreate
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/excel/lotes")
async def importar_lotes_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Importa lotes desde un archivo Excel.
    
    Formato esperado del Excel:
    - Columnas: Mesa, Fecha Corte, Referencia, Material, Color, Talla, Cantidad, Observaciones, Prioridad
    """
    try:
        # Leer el archivo Excel
        contents = await file.read()
        try:
            df = pd.read_excel(io.BytesIO(contents))
        except Exception:
            # Intentar con engine explicitamente (openpyxl) y capturar error
            try:
                df = pd.read_excel(io.BytesIO(contents), engine='openpyxl')
            except Exception as e:
                tb = traceback.format_exc()
                logger.error("Error leyendo Excel: %s", tb)
                raise HTTPException(status_code=400, detail=f"Error al leer el archivo Excel: {str(e)}\n{tb}")
        
        # Validar columnas requeridas
        required_columns = ['Referencia', 'Material', 'Color', 'Talla', 'Cantidad']
        # Registrar columnas detectadas para ayudar en depuración
        try:
            detected_cols = list(df.columns)
            logger.debug("Columnas detectadas en Excel: %s", detected_cols)
        except Exception:
            detected_cols = []
            logger.debug("No se pudieron obtener columnas del DataFrame")

        # Si las columnas vienen como 'Unnamed' intentar inferir encabezado
        def _norm(x):
            return re.sub(r"\s+", " ", str(x).strip().lower())

        try:
            if detected_cols and all(str(c).startswith('Unnamed') for c in detected_cols):
                logger.debug("Columnas son 'Unnamed' — intentando inferir encabezado desde la primera fila o header=1")
                try:
                    first_row = df.iloc[0].tolist()
                    norm_first = [_norm(v) for v in first_row]
                    norm_required = [_norm(c) for c in required_columns]
                    if set(norm_required).issubset(set(norm_first)):
                        df.columns = first_row
                        df = df.drop(index=0).reset_index(drop=True)
                        detected_cols = list(df.columns)
                        logger.debug("Usando primera fila como encabezado. Nuevas columnas: %s", detected_cols)
                    else:
                        # Intentar con header=1
                        try:
                            df_alt = pd.read_excel(io.BytesIO(contents), header=1, engine='openpyxl')
                        except Exception:
                            df_alt = pd.read_excel(io.BytesIO(contents), header=1)
                        alt_cols = list(df_alt.columns)
                        norm_alt = [_norm(c) for c in alt_cols]
                        if set(norm_required).issubset(set(norm_alt)):
                            df = df_alt
                            detected_cols = list(df.columns)
                            logger.debug("Usando header=1. Columnas: %s", detected_cols)
                except Exception as e:
                    logger.debug("No se pudo inferir encabezado automáticamente: %s", str(e))
        except Exception:
            pass

        missing_columns = [col for col in required_columns if col not in detected_cols]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Faltan las siguientes columnas: {', '.join(missing_columns)}. Columnas detectadas: {detected_cols}"
            )
        
        lotes_creados = []
        errores = []
        
        # Agrupar por lote (Mesa + Referencia + Material + Fecha)
        df['Fecha Corte'] = pd.to_datetime(df.get('Fecha Corte', datetime.now()))
        df['Mesa'] = df.get('Mesa', '')
        df['Numero Lote'] = df.apply(
            lambda row: f"{row.get('Mesa', 'M')}-{row['Referencia']}-{row['Material']}-{row['Fecha Corte'].strftime('%Y%m%d')}",
            axis=1
        )
        
        grupos = df.groupby(['Numero Lote', 'Referencia', 'Material', 'Fecha Corte', 'Mesa', 'Observaciones', 'Prioridad'])
        
        for (numero_lote, referencia_nombre, material_nombre, fecha_corte, mesa, observaciones, prioridad), grupo in grupos:
            try:
                # Buscar o crear referencia
                referencia = db.query(Referencia).filter(
                    Referencia.codigo == referencia_nombre
                ).first()
                if not referencia:
                    referencia = db.query(Referencia).filter(
                        Referencia.nombre.ilike(f"%{referencia_nombre}%")
                    ).first()
                if not referencia:
                    errores.append(f"Referencia '{referencia_nombre}' no encontrada para lote {numero_lote}")
                    continue
                
                # Buscar material
                material = db.query(Material).filter(
                    Material.codigo == material_nombre
                ).first()
                if not material:
                    material = db.query(Material).filter(
                        Material.nombre.ilike(f"%{material_nombre}%")
                    ).first()
                if not material:
                    errores.append(f"Material '{material_nombre}' no encontrado para lote {numero_lote}")
                    continue
                
                # Verificar si el lote ya existe
                lote_existente = db.query(Lote).filter(Lote.numero_lote == numero_lote).first()
                if lote_existente:
                    errores.append(f"Lote {numero_lote} ya existe")
                    continue
                
                # Crear detalles del lote
                detalles = []
                for _, row in grupo.iterrows():
                    # Obtener nombre del color (buscar en catálogo o usar el valor directamente)
                    color_nombre = str(row['Color']).strip()
                    color = db.query(Color).filter(
                        Color.codigo == color_nombre
                    ).first()
                    if not color:
                        color = db.query(Color).filter(
                            Color.nombre.ilike(f"%{color_nombre}%")
                        ).first()
                    if color:
                        color_nombre = color.nombre  # Usar el nombre del catálogo si existe
                    
                    # Buscar talla
                    talla = db.query(Talla).filter(
                        Talla.codigo == row['Talla']
                    ).first()
                    if not talla:
                        talla = db.query(Talla).filter(
                            Talla.nombre.ilike(f"%{row['Talla']}%")
                        ).first()
                    if not talla:
                        errores.append(f"Talla '{row['Talla']}' no encontrada")
                        continue
                    
                    detalles.append({
                        'color_nombre': color_nombre,
                        'talla_id': talla.id,
                        'cantidad': int(row['Cantidad'])
                    })
                
                if not detalles:
                    errores.append(f"No se pudieron crear detalles para lote {numero_lote}")
                    continue
                
                # Crear el lote
                lote_data = LoteCreate(
                    numero_lote=numero_lote,
                    mesa=mesa if pd.notna(mesa) else None,
                    referencia_id=referencia.id,
                    material_id=material.id,
                    fecha_corte=fecha_corte if isinstance(fecha_corte, datetime) else datetime.now(),
                    observaciones=observaciones if pd.notna(observaciones) else None,
                    prioridad=int(prioridad) if pd.notna(prioridad) else 0,
                    detalles=[LoteDetalleCreate(**d) for d in detalles]
                )
                
                # Crear el lote en la base de datos
                cantidad_total = sum(d['cantidad'] for d in detalles)
                lote_dict = lote_data.model_dump(exclude={"detalles"})
                lote_dict["cantidad_total_programada"] = cantidad_total
                db_lote = Lote(**lote_dict)
                db.add(db_lote)
                db.flush()
                
                # Crear detalles
                for detalle in lote_data.detalles:
                    db_detalle = LoteDetalle(lote_id=db_lote.id, **detalle.model_dump())
                    db.add(db_detalle)
                
                db.commit()
                db.refresh(db_lote)
                lotes_creados.append(numero_lote)
                
            except Exception as e:
                errores.append(f"Error procesando lote {numero_lote}: {str(e)}")
                db.rollback()
                continue
        
        return {
            "mensaje": f"Importación completada",
            "lotes_creados": len(lotes_creados),
            "lotes": lotes_creados,
            "errores": errores,
            "total_errores": len(errores)
        }
        
    except HTTPException:
        # Re-lanzar HTTPExceptions sin modificar
        raise
    except Exception as e:
        tb = traceback.format_exc()
        logger.error("Excepción importación lotes: %s", tb)
        raise HTTPException(status_code=400, detail=f"Error al procesar el archivo: {str(e)}\n{tb}")


