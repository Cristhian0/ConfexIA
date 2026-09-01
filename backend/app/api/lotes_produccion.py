from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models import Lote, LoteDetalle
from app.models.lote import EstadoLote
from app.schemas.lote import LoteCreate, LoteUpdate, LoteResponse, LoteDetalleResponse
from app.core.business_rules import validar_lote_producto_unico

router = APIRouter()

def agregar_nombres_a_lote(lote: Lote) -> Lote:
    """Agrega los nombres de referencia y material al objeto Lote"""
    # Asegurar que las relaciones estén cargadas
    if lote.referencia:
        nombre_ref = lote.referencia.nombre or lote.referencia.codigo
        setattr(lote, 'referencia_nombre', nombre_ref)
        
        lote.__dict__['referencia_nombre'] = nombre_ref
    if lote.material:
        nombre_mat = lote.material.nombre or lote.material.codigo
        setattr(lote, 'material_nombre', nombre_mat)
       
        lote.__dict__['material_nombre'] = nombre_mat
    # Asegurar que los campos nuevos estén presentes en el dict para la serialización
    try:
        if hasattr(lote, 'confeccionista_nombre') and lote.confeccionista_nombre:
            lote.__dict__['confeccionista_nombre'] = lote.confeccionista_nombre
        if hasattr(lote, 'remision_numero') and lote.remision_numero:
            lote.__dict__['remision_numero'] = lote.remision_numero
        if hasattr(lote, 'fecha_entrega') and lote.fecha_entrega:
            lote.__dict__['fecha_entrega'] = lote.fecha_entrega
        if hasattr(lote, 'fecha_entrega_estimada') and lote.fecha_entrega_estimada:
            lote.__dict__['fecha_entrega_estimada'] = lote.fecha_entrega_estimada
        if hasattr(lote, 'despacha'):
            lote.__dict__['despacha'] = lote.despacha
    except Exception:
        pass
    return lote

@router.get("/", response_model=List[LoteResponse])
def listar_lotes(
    skip: int = 0,
    limit: int = 100,
    estado: Optional[EstadoLote] = None,
    es_pedido_especial: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Lote).options(
        joinedload(Lote.referencia),
        joinedload(Lote.material),
        joinedload(Lote.detalles)
    )
    if estado:
        query = query.filter(Lote.estado == estado)
    if es_pedido_especial is not None:
        query = query.filter(Lote.es_pedido_especial == es_pedido_especial)
    lotes = query.order_by(Lote.created_at.desc()).offset(skip).limit(limit).all()
    # Agregar nombres a cada lote antes de la serialización
    for lote in lotes:
        agregar_nombres_a_lote(lote)
        # Forzar que los atributos estén disponibles para Pydantic
        if lote.referencia:
            nombre_ref = lote.referencia.nombre or lote.referencia.codigo
            lote.__dict__['referencia_nombre'] = nombre_ref
            setattr(lote, 'referencia_nombre', nombre_ref)
        if lote.material:
            nombre_mat = lote.material.nombre or lote.material.codigo
            lote.__dict__['material_nombre'] = nombre_mat
            setattr(lote, 'material_nombre', nombre_mat)
    return lotes

@router.post("/", response_model=LoteResponse, status_code=status.HTTP_201_CREATED)
def crear_lote(lote: LoteCreate, db: Session = Depends(get_db)):
    from app.models import Referencia, Material
    
    # Debug: Ver qué se está recibiendo
    print(f"DEBUG - Lote recibido: referencia_nombre='{lote.referencia_nombre}', material_nombre='{lote.material_nombre}'")
    print(f"DEBUG - Tipo de referencia_nombre: {type(lote.referencia_nombre)}, Tipo de material_nombre: {type(lote.material_nombre)}")
    
    # Verificar que el número de lote no exista
    if db.query(Lote).filter(Lote.numero_lote == lote.numero_lote).first():
        raise HTTPException(status_code=400, detail="El número de lote ya existe")
    
    # Validar que los nombres no estén vacíos
    referencia_nombre_str = str(lote.referencia_nombre).strip() if lote.referencia_nombre else ""
    material_nombre_str = str(lote.material_nombre).strip() if lote.material_nombre else ""
    
    if not referencia_nombre_str:
        raise HTTPException(status_code=400, detail="El nombre de referencia es requerido")
    
    if not material_nombre_str:
        raise HTTPException(status_code=400, detail="El nombre de material es requerido")
    
    # Convertir nombres a IDs - buscar por nombre exacto primero, luego por código, luego búsqueda flexible
    nombre_ref = referencia_nombre_str
    print(f"DEBUG - Buscando referencia con nombre: '{nombre_ref}'")
    
    # Intentar buscar por ID primero (por si acaso viene como número)
    referencia = None
    if nombre_ref.isdigit():
        referencia = db.query(Referencia).filter(Referencia.id == int(nombre_ref)).first()
        if referencia:
            print(f"DEBUG - Referencia encontrada por ID: {referencia.nombre}")
    
    if not referencia:
        # Buscar por nombre exacto
        referencia = db.query(Referencia).filter(Referencia.nombre == nombre_ref).first()
        if referencia:
            print(f"DEBUG - Referencia encontrada por nombre exacto: {referencia.nombre}")
    
    if not referencia:
        # Intentar buscar por código
        referencia = db.query(Referencia).filter(Referencia.codigo == nombre_ref).first()
        if referencia:
            print(f"DEBUG - Referencia encontrada por código: {referencia.nombre}")
    
    if not referencia:
        # Buscar con LIKE (case-insensitive) en nombre
        referencia = db.query(Referencia).filter(Referencia.nombre.ilike(f"%{nombre_ref}%")).first()
        if referencia:
            print(f"DEBUG - Referencia encontrada por LIKE: {referencia.nombre}")
    
    if not referencia:
        # Si no existe, crear la referencia automáticamente
        print(f"DEBUG - Referencia '{nombre_ref}' no encontrada. Creando automáticamente...")
        # Generar un código único basado en el nombre
        codigo_ref = nombre_ref.upper().replace(' ', '-')[:20]
        # Verificar que el código no exista
        contador = 1
        codigo_final = codigo_ref
        while db.query(Referencia).filter(Referencia.codigo == codigo_final).first():
            codigo_final = f"{codigo_ref}-{contador}"
            contador += 1
        
        referencia = Referencia(
            codigo=codigo_final,
            nombre=nombre_ref,
            descripcion=f"Referencia creada automáticamente: {nombre_ref}",
            activo=True,
            es_pedido_especial=False
        )
        db.add(referencia)
        db.flush()
        print(f"DEBUG - Referencia creada: ID={referencia.id}, Código={referencia.codigo}, Nombre={referencia.nombre}")
    
    nombre_mat = material_nombre_str
    print(f"DEBUG - Buscando material con nombre: '{nombre_mat}'")
    
    # Intentar buscar por ID primero (por si acaso viene como número)
    material = None
    if nombre_mat.isdigit():
        material = db.query(Material).filter(Material.id == int(nombre_mat)).first()
        if material:
            print(f"DEBUG - Material encontrado por ID: {material.nombre}")
    
    if not material:
        # Buscar por nombre exacto
        material = db.query(Material).filter(Material.nombre == nombre_mat).first()
        if material:
            print(f"DEBUG - Material encontrado por nombre exacto: {material.nombre}")
    
    if not material:
        # Intentar buscar por código
        material = db.query(Material).filter(Material.codigo == nombre_mat).first()
        if material:
            print(f"DEBUG - Material encontrado por código: {material.nombre}")
    
    if not material:
        # Buscar con LIKE (case-insensitive) en nombre
        material = db.query(Material).filter(Material.nombre.ilike(f"%{nombre_mat}%")).first()
        if material:
            print(f"DEBUG - Material encontrado por LIKE: {material.nombre}")
    
    if not material:
        # Si no existe, crear el material automáticamente
        print(f"DEBUG - Material '{nombre_mat}' no encontrado. Creando automáticamente...")
        # Generar un código único basado en el nombre
        codigo_mat = nombre_mat.upper().replace(' ', '-').replace('á', 'A').replace('é', 'E').replace('í', 'I').replace('ó', 'O').replace('ú', 'U')[:20]
        # Verificar que el código no exista
        contador = 1
        codigo_final = codigo_mat
        while db.query(Material).filter(Material.codigo == codigo_final).first():
            codigo_final = f"{codigo_mat}-{contador}"
            contador += 1
        
        material = Material(
            codigo=codigo_final,
            nombre=nombre_mat,
            descripcion=f"Material creado automáticamente: {nombre_mat}",
            activo=True
        )
        db.add(material)
        db.flush()
        print(f"DEBUG - Material creado: ID={material.id}, Código={material.codigo}, Nombre={material.nombre}")
    
    # Validar que todos los detalles tengan color_nombre y talla_id
    for detalle in lote.detalles:
        if not detalle.color_nombre or not detalle.color_nombre.strip():
            raise HTTPException(
                status_code=400, 
                detail="Todos los detalles deben incluir un nombre de color válido"
            )
        if not detalle.talla_id or detalle.talla_id <= 0:
            raise HTTPException(
                status_code=400, 
                detail="Todos los detalles deben incluir un talla_id válido"
            )
        if not detalle.cantidad or detalle.cantidad <= 0:
            raise HTTPException(
                status_code=400, 
                detail="Todos los detalles deben tener una cantidad mayor a 0"
            )
    
    # Calcular cantidad total programada si no se proporciona
    cantidad_total = lote.cantidad_total_programada
    if not cantidad_total:
        cantidad_total = sum(d.cantidad for d in lote.detalles)
    
    # Crear el lote - convertir nombres a IDs
    print(f"DEBUG - Referencia encontrada: ID={referencia.id}, Nombre={referencia.nombre}")
    print(f"DEBUG - Material encontrado: ID={material.id}, Nombre={material.nombre}")
    
    # Obtener todos los datos excepto los nombres y detalles
    lote_data = lote.model_dump(exclude={"detalles", "referencia_nombre", "material_nombre"})
    
    # Asegurarse de que no haya IDs previos (por si acaso)
    lote_data.pop("referencia_id", None)
    lote_data.pop("material_id", None)
    
    # Asignar los IDs correctos
    lote_data["referencia_id"] = int(referencia.id)
    lote_data["material_id"] = int(material.id)
    
    print(f"DEBUG - Datos del lote a crear: referencia_id={lote_data.get('referencia_id')}, material_id={lote_data.get('material_id')}")
    print(f"DEBUG - Todos los campos del lote_data: {list(lote_data.keys())}")
    
    # Asegurar tipos correctos y limpiar valores None
    # Convertir es_pedido_especial a boolean explícitamente
    es_pedido_especial = lote_data.get("es_pedido_especial")
    if es_pedido_especial is None:
        lote_data["es_pedido_especial"] = False
    elif isinstance(es_pedido_especial, bool):
        lote_data["es_pedido_especial"] = es_pedido_especial
    elif isinstance(es_pedido_especial, (int, str)):
        lote_data["es_pedido_especial"] = bool(int(es_pedido_especial))
    else:
        lote_data["es_pedido_especial"] = False
    
    # Asegurar que prioridad sea int
    prioridad = lote_data.get("prioridad")
    if prioridad is None:
        lote_data["prioridad"] = 0
    else:
        lote_data["prioridad"] = int(prioridad)
    
    # Asegurar que cantidad_total_programada sea int
    lote_data["cantidad_total_programada"] = int(cantidad_total) if cantidad_total else 0

    # Incluir explícitamente los campos nuevos recibidos desde el schema
    lote_data["remision_numero"] = lote.remision_numero if hasattr(lote, 'remision_numero') else None
    lote_data["confeccionista_nombre"] = lote.confeccionista_nombre if hasattr(lote, 'confeccionista_nombre') else None
    lote_data["despacha"] = bool(lote.despacha) if hasattr(lote, 'despacha') and lote.despacha is not None else False
    lote_data["fecha_entrega"] = lote.fecha_entrega if hasattr(lote, 'fecha_entrega') else None
    lote_data["fecha_entrega_estimada"] = lote.fecha_entrega_estimada if hasattr(lote, 'fecha_entrega_estimada') else None
    
    # Limpiar campos opcionales - convertir strings vacíos a None
    if "mesa" in lote_data:
        mesa = lote_data["mesa"]
        if mesa is None or (isinstance(mesa, str) and mesa.strip() == ""):
            lote_data["mesa"] = None
    if "observaciones" in lote_data:
        obs = lote_data["observaciones"]
        if obs is None or (isinstance(obs, str) and obs.strip() == ""):
            lote_data["observaciones"] = None
    
    campos_a_remover = ["id", "created_at", "updated_at", "fecha_asignacion", "estado", "color_id"]
    for campo in campos_a_remover:
        lote_data.pop(campo, None)
    
    try:
        # Asegurar que fecha_corte sea un objeto datetime si viene como string
        if "fecha_corte" in lote_data and isinstance(lote_data["fecha_corte"], str):
            from datetime import datetime
            try:
                fecha_str = lote_data["fecha_corte"].replace('Z', '+00:00')
                lote_data["fecha_corte"] = datetime.fromisoformat(fecha_str)
            except:
                try:
                    lote_data["fecha_corte"] = datetime.fromisoformat(lote_data["fecha_corte"])
                except:
                    pass  # Dejar que SQLAlchemy maneje la conversión
        # Convertir fechas adicionales si vienen como strings ISO
        if "fecha_entrega" in lote_data and isinstance(lote_data["fecha_entrega"], str):
            try:
                lote_data["fecha_entrega"] = datetime.fromisoformat(lote_data["fecha_entrega"].replace('Z', '+00:00'))
            except:
                pass
        if "fecha_entrega_estimada" in lote_data and isinstance(lote_data["fecha_entrega_estimada"], str):
            try:
                lote_data["fecha_entrega_estimada"] = datetime.fromisoformat(lote_data["fecha_entrega_estimada"].replace('Z', '+00:00'))
            except:
                pass
        
        print(f"DEBUG - Creando lote con referencia_id={lote_data.get('referencia_id')} (tipo: {type(lote_data.get('referencia_id'))})")
        print(f"DEBUG - Creando lote con material_id={lote_data.get('material_id')} (tipo: {type(lote_data.get('material_id'))})")
        
        db_lote = Lote(**lote_data)
        print(f"DEBUG - Lote creado en memoria: referencia_id={db_lote.referencia_id}, material_id={db_lote.material_id}")
        db.add(db_lote)
        db.flush()  # Para obtener el ID del lote
        print(f"DEBUG - Lote guardado con ID={db_lote.id}, referencia_id={db_lote.referencia_id}, material_id={db_lote.material_id}")
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"Error al crear el lote: {error_detail}")
        print(f"Datos del lote: {lote_data}")
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error al crear el lote en la base de datos: {str(e)}"
        )
    
    # Crear los detalles del lote (cada detalle incluye color_nombre, talla y cantidad)
    try:
        for detalle in lote.detalles:
            detalle_data = detalle.model_dump()
            # Asegurar que los tipos sean correctos
            detalle_data["color_nombre"] = str(detalle_data["color_nombre"]).strip()
            detalle_data["talla_id"] = int(detalle_data["talla_id"])
            detalle_data["cantidad"] = int(detalle_data["cantidad"]) if detalle_data.get("cantidad") is not None else 0
            
            if not detalle_data["color_nombre"] or not detalle_data["talla_id"]:
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail="Todos los detalles deben tener color_nombre y talla_id válidos"
                )
            
            # Remover campos que no deben estar en la creación
            detalle_data.pop("id", None)
            detalle_data.pop("lote_id", None)
            detalle_data.pop("created_at", None)
            detalle_data.pop("updated_at", None)
            detalle_data.pop("cantidad_cortada", None)
            detalle_data.pop("cantidad_en_taller", None)
            detalle_data.pop("cantidad_confeccionada", None)
            detalle_data.pop("cantidad_entregada", None)
            
            db_detalle = LoteDetalle(lote_id=db_lote.id, **detalle_data)
            db.add(db_detalle)
        
        db.commit()
        db.refresh(db_lote)
        # Recargar con relaciones
        db_lote = db.query(Lote).options(
            joinedload(Lote.referencia),
            joinedload(Lote.material),
            joinedload(Lote.detalles)
        ).filter(Lote.id == db_lote.id).first()
        agregar_nombres_a_lote(db_lote)
        # Asegurar que los campos nuevos estén presentes en la respuesta (usar lote_data si hace falta)
        try:
            if lote_data.get('confeccionista_nombre'):
                db_lote.__dict__['confeccionista_nombre'] = lote_data.get('confeccionista_nombre')
            if lote_data.get('remision_numero'):
                db_lote.__dict__['remision_numero'] = lote_data.get('remision_numero')
            if lote_data.get('fecha_entrega'):
                db_lote.__dict__['fecha_entrega'] = lote_data.get('fecha_entrega')
            if lote_data.get('fecha_entrega_estimada'):
                db_lote.__dict__['fecha_entrega_estimada'] = lote_data.get('fecha_entrega_estimada')
            db_lote.__dict__['despacha'] = lote_data.get('despacha', False)
        except Exception:
            pass
        # Asegurar que los nombres estén en el dict
        if db_lote.referencia:
            db_lote.__dict__['referencia_nombre'] = db_lote.referencia.nombre or db_lote.referencia.codigo
        if db_lote.material:
            db_lote.__dict__['material_nombre'] = db_lote.material.nombre or db_lote.material.codigo
        return db_lote
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        import traceback
        error_detail = traceback.format_exc()
        print(f"Error detallado al crear lote: {error_detail}")
        raise HTTPException(status_code=500, detail=f"Error al crear el lote: {str(e)}")

@router.get("/{lote_id}", response_model=LoteResponse)
def obtener_lote(lote_id: int, db: Session = Depends(get_db)):
    lote = db.query(Lote).options(
        joinedload(Lote.referencia),
        joinedload(Lote.material)
    ).filter(Lote.id == lote_id).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    agregar_nombres_a_lote(lote)
    return lote

@router.put("/{lote_id}", response_model=LoteResponse)
def actualizar_lote(lote_id: int, lote: LoteUpdate, db: Session = Depends(get_db)):
    from app.models import Referencia, Material
    
    db_lote = db.query(Lote).options(
        joinedload(Lote.referencia),
        joinedload(Lote.material)
    ).filter(Lote.id == lote_id).first()
    if not db_lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    
    update_data = lote.model_dump(exclude_unset=True, exclude={"detalles", "referencia_nombre", "material_nombre"})
    
    # Convertir nombres a IDs si se proporcionan
    if lote.referencia_nombre:
        referencia = db.query(Referencia).filter(Referencia.nombre == lote.referencia_nombre).first()
        if not referencia:
            referencia = db.query(Referencia).filter(Referencia.codigo == lote.referencia_nombre).first()
        if not referencia:
            raise HTTPException(status_code=404, detail=f"Referencia '{lote.referencia_nombre}' no encontrada")
        update_data["referencia_id"] = referencia.id
    
    if lote.material_nombre:
        material = db.query(Material).filter(Material.nombre == lote.material_nombre).first()
        if not material:
            material = db.query(Material).filter(Material.codigo == lote.material_nombre).first()
        if not material:
            raise HTTPException(status_code=404, detail=f"Material '{lote.material_nombre}' no encontrado")
        update_data["material_id"] = material.id
    
    # Actualizar campos del lote
    for field, value in update_data.items():
        if field == "es_pedido_especial" and value is not None:
            # Asegurar que es boolean
            if isinstance(value, (int, str)):
                value = bool(int(value))
            setattr(db_lote, field, bool(value))
        elif field == "prioridad" and value is not None:
            setattr(db_lote, field, int(value))
        elif field == "cantidad_total_programada" and value is not None:
            setattr(db_lote, field, int(value))
        elif value is not None:
            setattr(db_lote, field, value)
    
    # Si se proporcionan detalles, actualizarlos
    if lote.detalles is not None:
        # Validar detalles
        for detalle in lote.detalles:
            if not detalle.color_nombre or not detalle.color_nombre.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Todos los detalles deben incluir un nombre de color válido"
                )
            if not detalle.talla_id or detalle.talla_id <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Todos los detalles deben incluir un talla_id válido"
                )
            if not detalle.cantidad or detalle.cantidad <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Todos los detalles deben tener una cantidad mayor a 0"
                )
        
        # Eliminar detalles existentes
        for detalle_existente in db_lote.detalles:
            db.delete(detalle_existente)
        
        # Crear nuevos detalles
        cantidad_total = sum(d.cantidad for d in lote.detalles)
        if not update_data.get("cantidad_total_programada"):
            db_lote.cantidad_total_programada = cantidad_total
        
        for detalle in lote.detalles:
            detalle_data = detalle.model_dump()
            detalle_data["color_nombre"] = str(detalle_data["color_nombre"]).strip()
            detalle_data["talla_id"] = int(detalle_data["talla_id"])
            detalle_data["cantidad"] = int(detalle_data["cantidad"])
            
            # Remover campos que no deben estar
            detalle_data.pop("id", None)
            detalle_data.pop("lote_id", None)
            detalle_data.pop("created_at", None)
            detalle_data.pop("updated_at", None)
            detalle_data.pop("cantidad_cortada", None)
            detalle_data.pop("cantidad_en_taller", None)
            detalle_data.pop("cantidad_confeccionada", None)
            detalle_data.pop("cantidad_entregada", None)
            
            db_detalle = LoteDetalle(lote_id=db_lote.id, **detalle_data)
            db.add(db_detalle)
    
    try:
        db.commit()
        db.refresh(db_lote)
        # Recargar con relaciones
        db_lote = db.query(Lote).options(
            joinedload(Lote.referencia),
            joinedload(Lote.material),
            joinedload(Lote.detalles)
        ).filter(Lote.id == lote_id).first()
        agregar_nombres_a_lote(db_lote)
        # Asegurar que los nombres estén en el dict
        if db_lote.referencia:
            db_lote.__dict__['referencia_nombre'] = db_lote.referencia.nombre or db_lote.referencia.codigo
        if db_lote.material:
            db_lote.__dict__['material_nombre'] = db_lote.material.nombre or db_lote.material.codigo
        return db_lote
    except Exception as e:
        db.rollback()
        import traceback
        error_detail = traceback.format_exc()
        print(f"Error al actualizar lote: {error_detail}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar el lote: {str(e)}")

@router.delete("/{lote_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_lote(lote_id: int, db: Session = Depends(get_db)):
    lote = db.query(Lote).filter(Lote.id == lote_id).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    db.delete(lote)
    db.commit()
    return None

@router.get("/{lote_id}/detalles", response_model=List[LoteDetalleResponse])
def obtener_detalles_lote(lote_id: int, db: Session = Depends(get_db)):
    lote = db.query(Lote).filter(Lote.id == lote_id).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    return lote.detalles

@router.patch("/{lote_id}/estado", response_model=LoteResponse)
def actualizar_estado_lote(lote_id: int, estado: dict, db: Session = Depends(get_db)):
    estado_value = estado.get("estado") if isinstance(estado, dict) else estado
    if isinstance(estado_value, str):
        estado_value = EstadoLote(estado_value)
    db_lote = db.query(Lote).options(
        joinedload(Lote.referencia),
        joinedload(Lote.material)
    ).filter(Lote.id == lote_id).first()
    if not db_lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    
    db_lote.estado = estado_value
    if estado_value == EstadoLote.CORTE_COMPLETADO:
        # Actualizar cantidad_cortada en los detalles
        for detalle in db_lote.detalles:
            detalle.cantidad_cortada = detalle.cantidad
    
    db.commit()
    db.refresh(db_lote)
    # Recargar con relaciones
    db_lote = db.query(Lote).options(
        joinedload(Lote.referencia),
        joinedload(Lote.material),
        joinedload(Lote.detalles)
    ).filter(Lote.id == lote_id).first()
    agregar_nombres_a_lote(db_lote)
    # Asegurar que los nombres estén en el dict
    if db_lote.referencia:
        db_lote.__dict__['referencia_nombre'] = db_lote.referencia.nombre or db_lote.referencia.codigo
    if db_lote.material:
        db_lote.__dict__['material_nombre'] = db_lote.material.nombre or db_lote.material.codigo
    return db_lote

