from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.corte import (
    OrdenCorte,
    OrdenCorteLinea,
    ReservaTela,
    EstadoOrdenCorte,
    EstadoReservaTela,
)
from app.models import Material, Color
from app.schemas.corte import (
    OrdenCorteCreate,
    OrdenCorteResponse,
    OrdenCorteLineaResponse,
    OrdenCorteUpdateTizado,
    OrdenCorteUpdateCorte,
    OrdenCorteUpdateSobrantes,
    ReservaTelaCreate,
    ReservaTelaResponse,
)

router = APIRouter()


def _orden_to_response(db: Session, oc: OrdenCorte) -> OrdenCorteResponse:
    db.refresh(oc)
    lineas = db.query(OrdenCorteLinea).filter(OrdenCorteLinea.orden_corte_id == oc.id).all()
    return OrdenCorteResponse(
        id=oc.id,
        numero_orden=oc.numero_orden,
        tipo_prenda=oc.tipo_prenda,
        estado=oc.estado,
        metros_tizado=oc.metros_tizado,
        rendimiento_pct=oc.rendimiento_pct,
        piezas_cortadas=oc.piezas_cortadas,
        capas_utilizadas=oc.capas_utilizadas,
        metros_sobrante=oc.metros_sobrante,
        metros_desperdicio=oc.metros_desperdicio,
        observaciones=oc.observaciones,
        lineas=[OrdenCorteLineaResponse.model_validate(x) for x in lineas],
        created_at=oc.created_at,
        updated_at=oc.updated_at,
    )


@router.get("/ordenes", response_model=List[OrdenCorteResponse])
def listar_ordenes(skip: int = 0, limit: int = 200, db: Session = Depends(get_db)):
    rows = (
        db.query(OrdenCorte).order_by(OrdenCorte.id.desc()).offset(skip).limit(limit).all()
    )
    return [_orden_to_response(db, oc) for oc in rows]


@router.get("/ordenes/{orden_id}", response_model=OrdenCorteResponse)
def obtener_orden(orden_id: int, db: Session = Depends(get_db)):
    oc = db.query(OrdenCorte).filter(OrdenCorte.id == orden_id).first()
    if not oc:
        raise HTTPException(status_code=404, detail="Orden de corte no encontrada")
    return _orden_to_response(db, oc)


@router.post("/ordenes", response_model=OrdenCorteResponse, status_code=status.HTTP_201_CREATED)
def crear_orden(data: OrdenCorteCreate, db: Session = Depends(get_db)):
    if data.numero_orden:
        exists = db.query(OrdenCorte).filter(OrdenCorte.numero_orden == data.numero_orden).first()
        if exists:
            raise HTTPException(status_code=400, detail="Ya existe una orden con ese número")

    oc = OrdenCorte(
        numero_orden=data.numero_orden or "TEMP",
        tipo_prenda=data.tipo_prenda,
        estado=EstadoOrdenCorte.BORRADOR,
        observaciones=data.observaciones,
    )
    db.add(oc)
    db.flush()

    if not data.numero_orden:
        oc.numero_orden = f"OC-{oc.id:06d}"

    for ln in data.lineas:
        db.add(
            OrdenCorteLinea(
                orden_corte_id=oc.id,
                talla_codigo=ln.talla_codigo.strip().upper(),
                cantidad=ln.cantidad,
            )
        )
    db.commit()
    db.refresh(oc)
    return _orden_to_response(db, oc)


@router.patch("/ordenes/{orden_id}/tizado", response_model=OrdenCorteResponse)
def registrar_tizado(orden_id: int, data: OrdenCorteUpdateTizado, db: Session = Depends(get_db)):
    oc = db.query(OrdenCorte).filter(OrdenCorte.id == orden_id).first()
    if not oc:
        raise HTTPException(status_code=404, detail="Orden de corte no encontrada")
    if data.metros_tizado is not None:
        oc.metros_tizado = data.metros_tizado
    if data.rendimiento_pct is not None:
        oc.rendimiento_pct = data.rendimiento_pct
    oc.estado = EstadoOrdenCorte.TIZADO
    db.commit()
    return _orden_to_response(db, oc)


@router.patch("/ordenes/{orden_id}/corte", response_model=OrdenCorteResponse)
def registrar_corte(orden_id: int, data: OrdenCorteUpdateCorte, db: Session = Depends(get_db)):
    oc = db.query(OrdenCorte).filter(OrdenCorte.id == orden_id).first()
    if not oc:
        raise HTTPException(status_code=404, detail="Orden de corte no encontrada")
    if data.piezas_cortadas is not None:
        oc.piezas_cortadas = data.piezas_cortadas
    if data.capas_utilizadas is not None:
        oc.capas_utilizadas = data.capas_utilizadas
    oc.estado = EstadoOrdenCorte.CORTADO
    db.commit()
    return _orden_to_response(db, oc)


@router.patch("/ordenes/{orden_id}/sobrantes", response_model=OrdenCorteResponse)
def registrar_sobrantes(orden_id: int, data: OrdenCorteUpdateSobrantes, db: Session = Depends(get_db)):
    oc = db.query(OrdenCorte).filter(OrdenCorte.id == orden_id).first()
    if not oc:
        raise HTTPException(status_code=404, detail="Orden de corte no encontrada")
    if data.metros_sobrante is not None:
        oc.metros_sobrante = data.metros_sobrante
    if data.metros_desperdicio is not None:
        oc.metros_desperdicio = data.metros_desperdicio
    db.commit()
    return _orden_to_response(db, oc)


@router.get("/reservas", response_model=List[ReservaTelaResponse])
def listar_reservas(skip: int = 0, limit: int = 200, db: Session = Depends(get_db)):
    """RF-03: Listar reservas de tela para producción"""
    reservas = db.query(ReservaTela).order_by(ReservaTela.id.desc()).offset(skip).limit(limit).all()
    
    result = []
    for r in reservas:
        result.append(
            ReservaTelaResponse(
                id=r.id,
                material_id=r.material_id,
                color_id=r.color_id,
                metros=r.metros,
                orden_corte_id=r.orden_corte_id,
                estado=r.estado,
                observaciones=r.observaciones,
                material_nombre=r.material.nombre if r.material else None,
                color_nombre=r.color.nombre if r.color else None,
                orden_corte_numero=r.orden_corte.numero_orden if r.orden_corte else None,
                created_at=r.created_at,
            )
        )
    return result


@router.post("/reservas", response_model=ReservaTelaResponse, status_code=status.HTTP_201_CREATED)
def crear_reserva(data: ReservaTelaCreate, db: Session = Depends(get_db)):
    if not db.query(Material).filter(Material.id == data.material_id).first():
        raise HTTPException(status_code=404, detail="Material no encontrado")
    if not db.query(Color).filter(Color.id == data.color_id).first():
        raise HTTPException(status_code=404, detail="Color no encontrado")
    if data.orden_corte_id is not None:
        if not db.query(OrdenCorte).filter(OrdenCorte.id == data.orden_corte_id).first():
            raise HTTPException(status_code=404, detail="Orden de corte no encontrada")

    # Verificar stock disponible (RF-03: reservar tela para producción)
    from app.models.bodega import RolloStock
    stock = db.query(RolloStock).filter(
        RolloStock.material_id == data.material_id,
        RolloStock.color_id == data.color_id
    ).first()

    if not stock:
        raise HTTPException(status_code=404, detail="No existe stock para este material/color")

    cantidad_disponible = stock.cantidad_actual - stock.cantidad_reservada
    if cantidad_disponible < data.metros:
        raise HTTPException(
            status_code=400,
            detail=f"Stock insuficiente. Disponible: {cantidad_disponible}, solicitado: {data.metros}"
        )

    # Crear la reserva y actualizar el stock
    r = ReservaTela(
        material_id=data.material_id,
        color_id=data.color_id,
        metros=data.metros,
        orden_corte_id=data.orden_corte_id,
        estado=EstadoReservaTela.ACTIVA,
        observaciones=data.observaciones,
    )
    db.add(r)

    # Actualizar cantidad reservada en el stock
    stock.cantidad_reservada = stock.cantidad_reservada + data.metros

    db.commit()
    db.refresh(r)
    return ReservaTelaResponse(
        id=r.id,
        material_id=r.material_id,
        color_id=r.color_id,
        metros=r.metros,
        orden_corte_id=r.orden_corte_id,
        estado=r.estado,
        observaciones=r.observaciones,
        material_nombre=r.material.nombre if r.material else None,
        color_nombre=r.color.nombre if r.color else None,
        orden_corte_numero=r.orden_corte.numero_orden if r.orden_corte else None,
        created_at=r.created_at,
    )


@router.put("/reservas/{reserva_id}/liberar", response_model=ReservaTelaResponse)
def liberar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    """RF-03: Liberar reserva de tela (la tela vuelve a estar disponible)"""
    from app.models.bodega import RolloStock, RolloMovimiento, TipoMovimientoRollo
    
    reserva = db.query(ReservaTela).filter(ReservaTela.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    if reserva.estado != EstadoReservaTela.ACTIVA:
        raise HTTPException(status_code=400, detail="La reserva no está activa")

    # Liberar la reserva: reducir cantidad_reservada en el stock
    stock = db.query(RolloStock).filter(
        RolloStock.material_id == reserva.material_id,
        RolloStock.color_id == reserva.color_id
    ).first()

    if stock:
        stock.cantidad_reservada = max(0, stock.cantidad_reservada - reserva.metros)
        
        # Registrar movimiento de liberación de reserva
        movimiento = RolloMovimiento(
            rollo_stock_id=stock.id,
            tipo=TipoMovimientoRollo.AJUSTE,
            cantidad=-reserva.metros,  # Negativo para indicar liberación
            descripcion=f"Liberación de reserva #{reserva.id} (Orden: {reserva.orden_corte.numero_orden if reserva.orden_corte else 'N/A'})"
        )
        db.add(movimiento)

    # Cambiar estado de la reserva
    reserva.estado = EstadoReservaTela.CANCELADA
    db.commit()

    # Devolver respuesta con nombres
    db.refresh(reserva)
    return ReservaTelaResponse(
        id=reserva.id,
        material_id=reserva.material_id,
        color_id=reserva.color_id,
        metros=reserva.metros,
        orden_corte_id=reserva.orden_corte_id,
        estado=reserva.estado,
        observaciones=reserva.observaciones,
        material_nombre=reserva.material.nombre if reserva.material else None,
        color_nombre=reserva.color.nombre if reserva.color else None,
        orden_corte_numero=reserva.orden_corte.numero_orden if reserva.orden_corte else None,
        created_at=reserva.created_at,
    )


@router.put("/reservas/{reserva_id}/consumir", response_model=ReservaTelaResponse)
def consumir_reserva(reserva_id: int, db: Session = Depends(get_db)):
    """RF-03: Consumir reserva de tela (se usó en producción)"""
    from app.models.bodega import RolloStock, RolloMovimiento, TipoMovimientoRollo
    
    reserva = db.query(ReservaTela).filter(ReservaTela.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    if reserva.estado != EstadoReservaTela.ACTIVA:
        raise HTTPException(status_code=400, detail="La reserva no está activa")

    # Consumir la reserva: reducir cantidad_actual y cantidad_reservada en el stock
    stock = db.query(RolloStock).filter(
        RolloStock.material_id == reserva.material_id,
        RolloStock.color_id == reserva.color_id
    ).first()

    if stock:
        stock.cantidad_actual = max(0, stock.cantidad_actual - reserva.metros)
        stock.cantidad_reservada = max(0, stock.cantidad_reservada - reserva.metros)
        
        # Registrar movimiento de consumo
        movimiento = RolloMovimiento(
            rollo_stock_id=stock.id,
            tipo=TipoMovimientoRollo.SALIDA,
            cantidad=-reserva.metros,
            descripcion=f"Consumo de reserva #{reserva.id} para Orden: {reserva.orden_corte.numero_orden if reserva.orden_corte else 'N/A'}"
        )
        db.add(movimiento)

    # Cambiar estado de la reserva
    reserva.estado = EstadoReservaTela.CONSUMIDA
    db.commit()

    # Devolver respuesta con nombres
    db.refresh(reserva)
    return ReservaTelaResponse(
        id=reserva.id,
        material_id=reserva.material_id,
        color_id=reserva.color_id,
        metros=reserva.metros,
        orden_corte_id=reserva.orden_corte_id,
        estado=reserva.estado,
        observaciones=reserva.observaciones,
        material_nombre=reserva.material.nombre if reserva.material else None,
        color_nombre=reserva.color.nombre if reserva.color else None,
        orden_corte_numero=reserva.orden_corte.numero_orden if reserva.orden_corte else None,
        created_at=reserva.created_at,
    )


@router.get("/rollos/{rollo_id}/movimientos")
def listar_movimientos_rollo(rollo_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """RF-03: Obtener historial de movimientos de un rollo de tela"""
    from app.models.bodega import RolloStock, RolloMovimiento
    
    # Verificar que el rollo existe
    rollo = db.query(RolloStock).filter(RolloStock.id == rollo_id).first()
    if not rollo:
        raise HTTPException(status_code=404, detail="Rollo no encontrado")
    
    # Obtener movimientos ordenados por más reciente
    movimientos = db.query(RolloMovimiento).filter(
        RolloMovimiento.rollo_stock_id == rollo_id
    ).order_by(RolloMovimiento.created_at.desc()).offset(skip).limit(limit).all()
    
    resultado = []
    for mov in movimientos:
        resultado.append({
            "id": mov.id,
            "tipo": mov.tipo,
            "cantidad": mov.cantidad,
            "descripcion": mov.descripcion,
            "created_at": mov.created_at,
        })
    
    return resultado


@router.get("/tela/{material_id}/{color_id}/movimientos")
def listar_movimientos_tela(material_id: int, color_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """RF-03: Obtener historial de movimientos para un material y color específicos"""
    from app.models.bodega import RolloStock, RolloMovimiento
    
    # Verificar que el stock existe
    stock = db.query(RolloStock).filter(
        RolloStock.material_id == material_id,
        RolloStock.color_id == color_id
    ).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock no encontrado")
    
    # Obtener movimientos del rollo
    movimientos = db.query(RolloMovimiento).filter(
        RolloMovimiento.rollo_stock_id == stock.id
    ).order_by(RolloMovimiento.created_at.desc()).offset(skip).limit(limit).all()
    
    resultado = []
    for mov in movimientos:
        resultado.append({
            "id": mov.id,
            "tipo": mov.tipo,
            "cantidad": mov.cantidad,
            "descripcion": mov.descripcion,
            "created_at": mov.created_at,
        })
    
    return resultado
