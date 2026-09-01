"""
Validaciones de Reglas de Negocio
Centraliza todas las reglas de negocio del sistema textil
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from typing import Optional, List
from datetime import datetime

# ===== REGLA 1: No cerrar orden de producción con calidad pendiente =====
def validar_cierre_orden_produccion(db: Session, orden_produccion_id: int) -> None:
    """
    RN-1: No se puede cerrar una orden de producción si tiene inspección de calidad pendiente.
    Verifica que no haya inspecciones pendientes de aprobación/rechazo.
    """
    from app.models.produccion import InspeccionCalidad, ClasificacionInspeccion, OrdenProduccion
    
    # Obtener la orden
    orden = db.query(OrdenProduccion).filter(OrdenProduccion.id == orden_produccion_id).first()
    if not orden:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden de producción no encontrada"
        )
    
    # Verificar si hay inspecciones pendientes (sin clasificación final)
    inspecciones_pendientes = db.query(InspeccionCalidad).filter(
        InspeccionCalidad.orden_produccion_id == orden_produccion_id,
        InspeccionCalidad.clasificacion.notin_([
            ClasificacionInspeccion.OK if hasattr(ClasificacionInspeccion, 'OK') else None
        ])
    ).count()
    
    # Si hay inspecciones sin aprobar/rechazar definitivamente
    inspecciones_sin_clasificar = db.query(InspeccionCalidad).filter(
        InspeccionCalidad.orden_produccion_id == orden_produccion_id,
        InspeccionCalidad.clasificacion == None
    ).count()
    
    if inspecciones_sin_clasificar > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede cerrar la orden. Existen inspecciones de calidad pendiente de clasificación."
        )


# ===== REGLA 2: No despachar remisión sin stock disponible =====
def validar_stock_disponible_remision(db: Session, remision_id: int) -> bool:
    """
    RN-2: No se puede despachar una remisión si no hay stock disponible.
    Verifica que todos los items de la remisión tengan stock en bodega.
    """
    from app.models import Remision, RemisionDetalle
    from app.models.bodega import RolloStock, ReservaStock
    
    remision = db.query(Remision).filter(Remision.id == remision_id).first()
    if not remision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remisión no encontrada"
        )
    
    detalles = db.query(RemisionDetalle).filter(RemisionDetalle.remision_id == remision_id).all()
    
    for detalle in detalles:
        # Obtener stock disponible (sin compromisos)
        stock = db.query(RolloStock).filter(
            RolloStock.material_id == detalle.material_id,
            RolloStock.color_id == detalle.color_id
        ).first()
        
        if not stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No hay stock disponible para material_id={detalle.material_id}, color_id={detalle.color_id}"
            )
        
        # Calcular disponible = actual - reservado
        disponible = stock.cantidad_actual - stock.cantidad_reservada
        
        if disponible < detalle.cantidad_solicitada:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente para material {detalle.material_id}, color {detalle.color_id}. "
                        f"Disponible: {disponible}, Solicitado: {detalle.cantidad_solicitada}"
            )
    
    return True


# ===== REGLA 3: No permitir metros negativos en tela =====
def validar_metros_positivos_tela(
    db: Session,
    material_id: int,
    color_id: int,
    cantidad_salida: Decimal,
    lote_proveedor: Optional[str] = None
) -> None:
    """
    RN-3: Un rollo de tela no puede quedar con metros negativos.
    Valida que un movimiento de salida no deje el stock en negativo.
    
    Si lote_proveedor es None, valida contra la suma total de todos los stocks
    disponibles para ese material/color.
    """
    from app.models.bodega import RolloStock
    
    if lote_proveedor is not None:
        # Validar un lote específico (para ingresos)
        stock = db.query(RolloStock).filter(
            RolloStock.material_id == material_id,
            RolloStock.color_id == color_id,
            RolloStock.lote_proveedor == lote_proveedor
        ).first()
        
        if not stock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stock no encontrado para material_id={material_id}, color_id={color_id}, lote={lote_proveedor}"
            )
        
        metros_resultantes = stock.cantidad_actual - cantidad_salida
        if metros_resultantes < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede registrar salida. Stock actual del lote {lote_proveedor}: {stock.cantidad_actual} metros, "
                        f"Intento de salida: {cantidad_salida} metros. Resultaría en {metros_resultantes} metros negativos."
            )
    else:
        # Validar contra la suma total de todos los stocks (para salidas generales)
        from sqlalchemy import func
        total_stock = db.query(func.sum(RolloStock.cantidad_actual)).filter(
            RolloStock.material_id == material_id,
            RolloStock.color_id == color_id
        ).scalar() or 0
        
        if total_stock < cantidad_salida:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente. Stock total disponible: {total_stock} metros, "
                        f"Intento de salida: {cantidad_salida} metros."
            )


# ===== REGLA 4: Recalcular costo unitario del lote =====
def recalcular_costo_unitario_lote(db: Session, lote_id: int) -> Decimal:
    """
    RN-4: El costo unitario del lote debe recalcularse cada vez que cambie 
    costo de tela, insumos o mano de obra.
    
    Fórmula: Costo Total / Cantidad Total
    Costo Total = (Costo Tela) + (Costo Insumos) + (Costo Mano Obra)
    """
    from app.models import Lote, CostoLote
    
    lote = db.query(Lote).filter(Lote.id == lote_id).first()
    if not lote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lote no encontrado"
        )
    
    # Obtener costos del lote
    costo_record = db.query(CostoLote).filter(CostoLote.lote_id == lote_id).first()
    if not costo_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de costos no encontrado para este lote"
        )
    
    # Calcular costo total
    costo_tela = costo_record.costo_tela or Decimal(0)
    costo_insumos = costo_record.costo_insumos or Decimal(0)
    costo_mano_obra = costo_record.costo_mano_obra or Decimal(0)
    
    costo_total = costo_tela + costo_insumos + costo_mano_obra
    
    # Evitar división por cero
    cantidad_total = lote.cantidad_total_programada or 1
    
    costo_unitario = costo_total / cantidad_total
    
    # Actualizar el costo unitario
    costo_record.costo_unitario = costo_unitario
    costo_record.updated_at = datetime.now()
    
    db.add(costo_record)
    db.commit()
    
    return costo_unitario


# ===== REGLA 5: Variante de producto única por producto + color + talla =====
def validar_variante_unica_producto(
    db: Session,
    producto_id: int,
    color_id: int,
    talla_id: int,
    excluir_variante_id: Optional[int] = None
) -> None:
    """
    RN-5: Una variante de producto debe ser única por producto + color + talla.
    Verifica que no exista otra variante con la misma combinación.
    
    Nota: Esta validación aplica cuando exista modelo Variante.
    Actualmente puede aplicarse en nivel de lote/referencia/color/talla si es necesario.
    """
    # Intenta importar el modelo Variante si existe
    try:
        from app.models import Variante
        
        query = db.query(Variante).filter(
            Variante.producto_id == producto_id,
            Variante.color_id == color_id,
            Variante.talla_id == talla_id
        )
        
        # Si estamos actualizando, excluimos la variante actual
        if excluir_variante_id:
            query = query.filter(Variante.id != excluir_variante_id)
        
        existente = query.first()
        
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una variante con esta combinación de producto, color y talla."
            )
    except ImportError:
        # Si el modelo Variante no existe, la validación se puede implementar de forma diferente
        # Por ejemplo, a nivel de LoteDetalle con referencias
        pass


# ===== REGLA 6: Un lote debe pertenecer a un solo producto base =====
def validar_lote_producto_unico(db: Session, lote_id: int, producto_id: int) -> None:
    """
    RN-6: Un lote debe pertenecer a un solo producto base.
    Verifica que no se intente asignar productos diferentes al mismo lote.
    """
    from app.models import Lote, LoteDetalle, Referencia
    
    lote = db.query(Lote).filter(Lote.id == lote_id).first()
    if not lote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lote no encontrado"
        )
    
    # Obtener el producto base de la referencia actual del lote
    referencia = db.query(Referencia).filter(Referencia.id == lote.referencia_id).first()
    if not referencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referencia no encontrada"
        )
    
    # Si el lote ya tiene un producto asignado y es diferente, rechazar
    if hasattr(referencia, 'producto_id') and referencia.producto_id != producto_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El lote {lote.numero_lote} ya está asignado al producto {referencia.producto_id}. "
                    f"No se puede cambiar a producto {producto_id}."
        )


# ===== REGLA 7: Actualizar inventario de PT automáticamente al aprobar calidad =====
def actualizar_inventario_pt_por_calidad(
    db: Session,
    lote_id: int,
    cantidad_aprobada: int
) -> None:
    """
    RN-7: El inventario de producto terminado debe actualizarse automáticamente 
    al aprobar calidad.
    
    Suma las cantidades aprobadas en control de calidad al inventario PT.
    """
    from app.models import Lote, InventarioPT
    
    lote = db.query(Lote).filter(Lote.id == lote_id).first()
    if not lote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lote no encontrado"
        )
    
    # Obtener o crear registro de inventario PT
    referencia_id = lote.referencia_id
    inventario_pt = db.query(InventarioPT).filter(
        InventarioPT.referencia_id == referencia_id
    ).first()
    
    if not inventario_pt:
        # Crear nuevo registro
        inventario_pt = InventarioPT(
            referencia_id=referencia_id,
            cantidad_disponible=cantidad_aprobada,
            cantidad_reservada=0
        )
        db.add(inventario_pt)
    else:
        # Incrementar cantidad disponible
        inventario_pt.cantidad_disponible = (inventario_pt.cantidad_disponible or 0) + cantidad_aprobada
    
    inventario_pt.updated_at = datetime.now()
    db.commit()


# ===== Funciones auxiliares =====
def obtener_stock_disponible(db: Session, material_id: int, color_id: int) -> Decimal:
    """Calcula el stock disponible = actual - reservado"""
    from app.models.bodega import RolloStock
    
    stock = db.query(RolloStock).filter(
        RolloStock.material_id == material_id,
        RolloStock.color_id == color_id
    ).first()
    
    if not stock:
        return Decimal(0)
    
    return stock.cantidad_actual - stock.cantidad_reservada


def verificar_inspecciones_pendientes(db: Session, orden_produccion_id: int) -> int:
    """Cuenta inspecciones sin clasificación final"""
    from app.models.produccion import InspeccionCalidad
    
    return db.query(InspeccionCalidad).filter(
        InspeccionCalidad.orden_produccion_id == orden_produccion_id,
        InspeccionCalidad.clasificacion == None
    ).count()
