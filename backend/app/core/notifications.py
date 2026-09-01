from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

def send_notification_to_taller(taller: Any, remision: Any, detalles: list) -> bool:
    """Envía notificación al taller con la orden asignada.
    Incluye todos los datos del confeccionista y asignación.
    Currently logs the notification. In future this can send email/SMS/webhook.
    """
    try:
        # Obtener información adicional del lote y referencia si está disponible
        lote_info = {}
        if hasattr(remision, 'lote') and remision.lote:
            lote_info = {
                "lote_numero": remision.lote.numero_lote,
                "referencia_nombre": getattr(remision.lote.referencia, 'nombre', None) if hasattr(remision.lote, 'referencia') and remision.lote.referencia else None,
                "material_nombre": getattr(remision.lote.material, 'nombre', None) if hasattr(remision.lote, 'material') and remision.lote.material else None,
            }
        
        mensaje = {
            "taller_id": taller.id,
            "taller_nombre": getattr(taller, "nombre", None),
            "taller_contacto": getattr(taller, "contacto", None),
            "taller_telefono": getattr(taller, "telefono", None),
            "numero_remision": remision.numero_remision,
            "remision_id": remision.id,
            "fecha_remision": str(remision.fecha_remision),
            "fecha_entrega_estimada": str(remision.fecha_entrega_estimada) if remision.fecha_entrega_estimada else None,
            "observaciones": getattr(remision, "observaciones", None),
            **lote_info,
            "detalles": []
        }
        
        # Incluir información completa de cada detalle con datos del confeccionista
        for d in detalles:
            detalle_info = {
                "talla_id": d.talla_id,
                "cantidad": d.cantidad,
                "confeccionista_nombre": getattr(d, "confeccionista_nombre", None),
                "tipo_prenda": getattr(d, "tipo_prenda", None),
                "fecha_entrega_estimada": str(getattr(d, "fecha_entrega_estimada", None)) if getattr(d, "fecha_entrega_estimada", None) else None,
            }
            
            # Incluir información de la talla si está disponible
            if hasattr(d, 'talla') and d.talla:
                detalle_info["talla_codigo"] = getattr(d.talla, 'codigo', None)
                detalle_info["talla_nombre"] = getattr(d.talla, 'nombre', None)
            
            mensaje["detalles"].append(detalle_info)
        
        logger.info("=" * 80)
        logger.info("NOTIFICACIÓN ENVIADA AL TALLER")
        logger.info("=" * 80)
        logger.info(f"Taller: {mensaje['taller_nombre']} (ID: {mensaje['taller_id']})")
        logger.info(f"Contacto: {mensaje.get('taller_contacto', 'N/A')} - Tel: {mensaje.get('taller_telefono', 'N/A')}")
        logger.info(f"Remisión: {mensaje['numero_remision']}")
        if lote_info.get('lote_numero'):
            logger.info(f"Lote: {lote_info['lote_numero']}")
        if lote_info.get('referencia_nombre'):
            logger.info(f"Referencia: {lote_info['referencia_nombre']}")
        if lote_info.get('material_nombre'):
            logger.info(f"Material: {lote_info['material_nombre']}")
        logger.info(f"Fecha de Remisión: {mensaje['fecha_remision']}")
        if mensaje.get('fecha_entrega_estimada'):
            logger.info(f"Fecha Entrega Estimada (General): {mensaje['fecha_entrega_estimada']}")
        logger.info("-" * 80)
        logger.info("DETALLES DE ASIGNACIÓN:")
        for i, detalle in enumerate(mensaje["detalles"], 1):
            logger.info(f"  Detalle {i}:")
            talla = detalle.get(
            "talla_nombre",
                detalle.get("talla_codigo", f"ID: {detalle['talla_id']}")
            )
            logger.info(f"    - Talla: {talla}")
            logger.info(f"    - Cantidad: {detalle['cantidad']}")
            if detalle.get('confeccionista_nombre'):
                logger.info(f"    - Confeccionista: {detalle['confeccionista_nombre']}")
            if detalle.get('tipo_prenda'):
                logger.info(f"    - Tipo de Prenda: {detalle['tipo_prenda']}")
            if detalle.get('fecha_entrega_estimada'):
                logger.info(f"    - Fecha Entrega Estimada: {detalle['fecha_entrega_estimada']}")
        logger.info("=" * 80)
        
        # TODO: integrar con sistema de correo/HTTP webhook
        # Ejemplo: enviar_email(taller.email, "Nueva Orden de Trabajo", mensaje)
        # Ejemplo: enviar_webhook(taller.webhook_url, mensaje)
        
        return True
    except Exception as e:
        logger.exception("Error enviando notificación al taller: %s", e)
        return False
