"""
Endpoint de chat con IA para consultas y análisis detallados
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import json
import re

from app.core.ml_models import (
    predictor_demanda,
    detector_defectos,
    recomendador_inventario,
)
from app.db.database import get_db
from app.models.lote import Lote
from app.models.colilla import Colilla
from app.models.producto_terminado import ProductoTerminadoStock
from app.schemas.bodega import IngresoRolloCreate
from app.schemas.lote import LoteCreate
from app.schemas.colilla import ColillaCreate
from app.schemas.taller import TallerCreate, RemisionCreate
from app.schemas.producto_terminado import ProductoTerminadoStockCreate
from app.schemas.prediccion import (
    AnaliseDatos,
    InsightDashboard,
    AnomaliaDetectada,
    PuntoReorden,
    CantidadEconomicaOrden,
)
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class PreguntaChat(BaseModel):
    pregunta: str
    contexto: str = "general"


class Accion(BaseModel):
    tipo: str  # "navegar", "instrucciones", "crear", "registrar", "registrar_tela"
    titulo: str
    descripcion: str
    entidad: Optional[str] = None
    destino: Optional[str] = None  # ruta a navegar
    pasos: Optional[List[str]] = None  # pasos para completar la acción
    botones: Optional[List[dict]] = None  # botones a mostrar
    payload: Optional[dict] = None  # datos para ejecutar la acción


class AccionRequest(BaseModel):
    tipo: str
    titulo: str
    descripcion: Optional[str] = None
    entidad: Optional[str] = None
    destino: Optional[str] = None
    pasos: Optional[List[str]] = None
    payload: Optional[dict] = None


class RespuestaChat(BaseModel):
    pregunta: str
    respuesta: str
    tipo: str  # "demanda", "calidad", "inventario", "general", "ayuda_accion"
    informe_detallado: dict
    acciones: list = None  # lista de Acciones para mostrar
    sugerencias: list = None


def generar_informe_demanda(db: Session) -> dict:
    """Genera informe detallado de demanda"""
    try:
        lotes = db.query(Lote).filter(
            Lote.created_at >= datetime.now() - timedelta(days=30)
        ).all()

        if not lotes:
            return {
                "titulo": "Análisis de Demanda",
                "estado": "Sin datos",
                "detalles": "No hay registros de lotes en los últimos 30 días"
            }

        cantidades = [lote.cantidad_total_programada for lote in lotes if lote.cantidad_total_programada]
        promedio = sum(cantidades) / len(cantidades) if cantidades else 0

        predicciones = predictor_demanda.predecir(dias=7)

        return {
            "titulo": "Análisis de Demanda",
            "periodo": "Últimos 30 días",
            "total_lotes": len(lotes),
            "cantidad_promedio": round(promedio, 2),
            "cantidad_total": sum(cantidades),
            "variabilidad": f"{(max(cantidades) - min(cantidades)) if cantidades else 0}",
            "predicciones_7_dias": predicciones,
            "recomendaciones": [
                f"Demanda promedio detectada: {round(promedio, 0)} unidades/día",
                f"Total de lotes procesados: {len(lotes)}",
                "Mantener stock según predicciones de demanda futura"
            ]
        }

    except Exception as e:
        return {"error": str(e), "titulo": "Análisis de Demanda"}


def generar_informe_calidad(db: Session) -> dict:
    """Genera informe detallado de calidad"""
    try:
        colillas = db.query(Colilla).filter(
            Colilla.created_at >= datetime.now() - timedelta(days=30)
        ).all()

        if not colillas:
            return {
                "titulo": "Análisis de Calidad",
                "estado": "Sin datos",
                "detalles": "No hay registros de control de calidad"
            }

        total_inspecciones = len(colillas)
        defectuosas = sum(1 for c in colillas if c.defectuosa)
        tasa_defectos = (defectuosas / total_inspecciones * 100) if total_inspecciones > 0 else 0

        anomalias = detector_defectos.detectar_anomalias()

        return {
            "titulo": "Análisis de Calidad",
            "periodo": "Últimos 30 días",
            "total_inspecciones": total_inspecciones,
            "prendas_defectuosas": defectuosas,
            "tasa_defectos_porcentaje": round(tasa_defectos, 2),
            "tasa_conformidad": round(100 - tasa_defectos, 2),
            "anomalias_detectadas": len(anomalias),
            "estado": "Crítico" if tasa_defectos > 10 else "Alerta" if tasa_defectos > 5 else "Óptimo",
            "recomendaciones": [
                f"Tasa de defectos: {round(tasa_defectos, 2)}%",
                "Revisar procesos de confección si defectos > 5%" if tasa_defectos > 5 else "Calidad manteniéndose dentro de parámetros",
                f"Total de unidades inspeccionadas: {total_inspecciones}"
            ]
        }

    except Exception as e:
        return {"error": str(e), "titulo": "Análisis de Calidad"}


def generar_informe_inventario(db: Session) -> dict:
    """Genera informe detallado de inventario"""
    try:
        productos = db.query(ProductoTerminadoStock).all()

        if not productos:
            return {
                "titulo": "Análisis de Inventario",
                "estado": "Sin datos",
                "detalles": "No hay productos terminados registrados"
            }

        stock_total = sum(p.cantidad_actual for p in productos if p.cantidad_actual)
        valor_total = stock_total * 50  # Precio estimado por unidad
        stock_critico = sum(1 for p in productos if (p.cantidad_actual or 0) < 50)

        punto_reorden = recomendador_inventario.calcular_punto_reorden(
            demanda_promedio=100,
            lead_time_dias=7,
            desviacion_estandar=20
        )

        cantidad_economica = recomendador_inventario.recomendar_cantidad_orden(
            demanda_anual=max(stock_total * 12, 1),
            costo_orden=150,
            costo_mantenimiento=2
        )

        return {
            "titulo": "Análisis de Inventario",
            "total_productos": len(productos),
            "stock_total": stock_total,
            "valor_inventario": round(valor_total, 2),
            "productos_bajo_stock": stock_critico,
            "punto_reorden_recomendado": punto_reorden["punto_reorden"],
            "punto_reorden_detalle": punto_reorden,
            "cantidad_economica_orden": cantidad_economica,
            "rotacion_inventario": "Normal",
            "recomendaciones": [
                f"Stock total de {stock_total} unidades",
                f"Valor del inventario: ${valor_total}",
                f"Punto de reorden recomendado: {punto_reorden['punto_reorden']} unidades",
                f"Productos bajo stock crítico: {stock_critico}",
                f"Cantidad económica de orden sugerida: {cantidad_economica['cantidad_optima']} unidades"
            ]
        }

    except Exception as e:
        return {"error": str(e), "titulo": "Análisis de Inventario"}


def obtener_acciones_recomendadas(tipo: str, contexto: str) -> list:
    acciones = []
    destinos = {
        'demanda': '/lotes',
        'calidad': '/colillas',
        'inventario': '/bodega',
        'general': '/dashboard',
        'ayuda_accion': '/chat-ia'
    }
    destino = destinos.get(tipo, '/chat-ia')

    acciones.append(Accion(
        tipo='navegar',
        titulo='Abrir sección relacionada',
        descripcion='Ver la sección del módulo que contiene datos relacionados a tu pregunta.',
        destino=destino
    ).model_dump(exclude_none=True))

    if tipo == 'inventario':
        acciones.append(Accion(
            tipo='navegar',
            titulo='Revisar productos con bajo stock',
            descripcion='Abrir inventario y priorizar artículos en nivel crítico.',
            destino='/bodega'
        ).model_dump(exclude_none=True))

    if tipo == 'calidad':
        acciones.append(Accion(
            tipo='navegar',
            titulo='Ver colillas de calidad',
            descripcion='Abrir registro de colillas para analizar defectos y proporción de conformidad.',
            destino='/colillas'
        ).model_dump(exclude_none=True))

    if tipo == 'demanda':
        acciones.append(Accion(
            tipo='navegar',
            titulo='Ver lotes de producción',
            descripcion='Abrir la lista de lotes para identificar prioridad y carga de trabajo.',
            destino='/lotes'
        ).model_dump(exclude_none=True))

    return acciones


def generar_sugerencias_seguimiento(tipo: str, contexto: str) -> list:
    sugerencias_map = {
        'demanda': [
            '¿Qué acciones puedo tomar para optimizar la producción?',
            'Dame un pronóstico más detallado para los próximos 14 días',
            '¿Cuáles son los lotes con mayor prioridad?'
        ],
        'calidad': [
            '¿Qué defectos aparecen con más frecuencia?',
            '¿Cómo mejorar la conformidad del proceso?',
            '¿Qué acciones preventivas recomendarías?'
        ],
        'inventario': [
            '¿Qué productos están próximos a agotarse?',
            '¿Cuál es el punto de reorden recomendado?',
            '¿Necesito hacer un pedido de reposición?'
        ],
        'general': [
            'Dame un resumen ejecutivo de la operación',
            '¿Qué áreas requieren atención inmediata?',
            'Muéstrame los pasos para mejorar eficiencia'
        ],
        'ayuda_accion': [
            '¿Cómo creo una nueva orden de producción?',
            '¿Cómo registro una entrada de tela?',
            '¿Cómo genero una remisión?'
        ]
    }

    sugerencias = sugerencias_map.get(tipo, sugerencias_map['general']).copy()
    if contexto == 'dashboard' and 'Dame un resumen ejecutivo del dashboard' not in sugerencias:
        sugerencias.insert(0, 'Dame un resumen ejecutivo del dashboard')

    return sugerencias


def detectar_intencion_accion(pregunta: str) -> dict:
    """
    Detecta si el usuario está pidiendo ayuda para realizar una acción específica.
    Retorna dict con tipo de acción, destino, pasos y payload sugerido.
    """
    pregunta_lower = pregunta.lower()

    def extraer_numero(texto: str) -> Optional[int]:
        match = re.search(r"(\d+)(?:\s*(metros|m|unidades|uds|prendas)?)", texto)
        return int(match.group(1)) if match else None

    cantidad = extraer_numero(pregunta_lower)
    
    acciones_mapa = {
        ("talle", "taller"): {
            "tipo": "crear",
            "entidad": "talle",
            "destino": "/talleres",
            "titulo": "Crear un Taller",
            "pasos": [
                "1. Navega a la sección de Talleres",
                "2. Haz clic en el botón 'Nuevo Taller'",
                "3. Completa los campos: Nombre del taller, Ubicación, Contacto",
                "4. Ingresa el código de taller (único)",
                "5. Define la capacidad de producción",
                "6. Guarda los cambios"
            ],
            "instrucciones": "Un taller es una unidad de producción. Allí se registran las órdenes de confección y se rastrea el progreso de la producción.",
            "payload": {
                "data": {
                    "codigo": "TALLER_AUTOMATICO",
                    "nombre": "Taller automático",
                    "capacidad_diaria": cantidad or 0
                }
            }
        },
        ("orden", "lote", "produccion"): {
            "tipo": "crear",
            "entidad": "orden",
            "destino": "/lotes",
            "titulo": "Crear una Orden de Producción",
            "pasos": [
                "1. Ve a la sección de Lotes de Producción",
                "2. Haz clic en 'Nuevo Lote'",
                "3. Selecciona la referencia de producto",
                "4. Especifica la cantidad a producir",
                "5. Define la fecha de entrega",
                "6. Asigna los materiales necesarios",
                "7. Guarda la orden"
            ],
            "instrucciones": "Una orden de producción agrupa la fabricación de múltiples prendas del mismo tipo. Controla el flujo desde corte hasta confección.",
            "payload": {
                "data": {
                    "numero_lote": "AUTO-LOTE-001",
                    "referencia_nombre": "Referencia automática",
                    "material_nombre": "Material automático",
                    "fecha_corte": datetime.now().isoformat(),
                    "cantidad_total_programada": cantidad or 0,
                    "detalles": [
                        {
                            "color_nombre": "Color automático",
                            "talla_id": 1,
                            "cantidad": max(cantidad or 1, 1)
                        }
                    ]
                }
            }
        },
        ("tela", "genero", "material", "trama"): {
            "tipo": "registrar",
            "entidad": "tela",
            "destino": "/tela",
            "titulo": "Registrar Entrada de Tela",
            "pasos": [
                "1. Abre la sección de Inventario de Tela",
                "2. Ve a la pestaña 'Registrar Ingreso de Tela'",
                "3. Selecciona el material (algodón, poliéster, etc.)",
                "4. Elige el color",
                "5. Ingresa el código de lote del proveedor",
                "6. Especifica los metros recibidos",
                "7. Añade descripción si es necesario",
                "8. Haz clic en 'Registrar Ingreso'"
            ],
            "instrucciones": "Registra cada entrada de tela para mantener el control de inventario de materias primas actualizado.",
            "payload": {
                "data": {
                    "material_id": None,
                    "material_nombre": "Material automático",
                    "color_id": None,
                    "color_nombre": "Color automático",
                    "cantidad": cantidad or 0,
                    "lote_proveedor": "PROV_AUTOMATICO",
                    "descripcion": "Ingreso automático generado por IA"
                }
            }
        },
        ("producto terminado", "prenda", "producto", "confeccionar", "confeccion"): {
            "tipo": "registrar",
            "entidad": "producto",
            "destino": "/producto-terminado",
            "titulo": "Registrar Producto Terminado",
            "pasos": [
                "1. Ve a la sección de Producto Terminado",
                "2. Ve a 'Registrar Ingreso de Prendas'",
                "3. Ingresa el SKU del producto",
                "4. Especifica el tipo de prenda",
                "5. Selecciona la talla",
                "6. Elige el color",
                "7. Selecciona la zona de almacenamiento",
                "8. Ingresa la cantidad",
                "9. Guarda el registro"
            ],
            "instrucciones": "Los productos terminados se almacenan en zonas específicas para facilitar el picking y distribución.",
            "payload": {
                "data": {
                    "sku": "SKU_AUTOMATICO",
                    "tipo": "Prenda automática",
                    "talla_id": None,
                    "talla_nombre": "Talla automática",
                    "color_id": None,
                    "color_nombre": "Color automático",
                    "zona": "A1",
                    "cantidad_actual": cantidad or 0,
                    "descripcion": "Ingreso automático generado por IA"
                }
            }
        },
        ("remision", "remesa", "envio", "entrega"): {
            "tipo": "crear",
            "entidad": "remisión",
            "destino": "/remisiones",
            "titulo": "Crear una Remisión",
            "pasos": [
                "1. Ve a la sección de Remisiones",
                "2. Haz clic en 'Nueva Remisión'",
                "3. Selecciona el cliente o taller destino",
                "4. Selecciona los productos a incluir",
                "5. Especifica cantidades",
                "6. Revisa el total",
                "7. Genera la remisión"
            ],
            "instrucciones": "Una remisión es el documento que acompaña la entrega de productos a clientes o talleres.",
            "payload": {
                "data": {
                    "numero_remision": "REM_AUTOMATICO",
                    "lote_id": None,
                    "lote_numero": "LOTE_EXISTENTE_001",
                    "taller_id": None,
                    "taller_nombre": "Taller destino automático",
                    "fecha_remision": datetime.now().isoformat(),
                    "detalles": [
                        {
                            "talla_id": 1,
                            "cantidad": max(cantidad or 1, 1)
                        }
                    ]
                }
            }
        },
        ("colilla", "inspeccion", "calidad", "defecto"): {
            "tipo": "registrar",
            "entidad": "colilla",
            "destino": "/colillas",
            "titulo": "Registrar Colilla de Calidad",
            "pasos": [
                "1. Ve a la sección de Colillas",
                "2. Haz clic en 'Nueva Colilla'",
                "3. Selecciona el lote de producción",
                "4. Especifica cantidad inspeccionada",
                "5. Registra cantidad conforme",
                "6. Registra cantidad defectuosa",
                "7. Detalla tipos de defectos si hay",
                "8. Guarda la inspección"
            ],
            "instrucciones": "Las colillas registran la inspección de calidad de cada lote de producción.",
            "payload": {
                "data": {
                    "lote_id": None,
                    "lote_numero": "LOTE_EXISTENTE_001",
                    "taller_id": None,
                    "taller_nombre": "Taller destino automático",
                    "confeccionista_nombre": "Confeccionista automático",
                    "tipo_trabajo": "OTRO",
                    "cantidad_prendas": cantidad or 0,
                    "descripcion_trabajo": "Entrada automática generada por IA"
                }
            }
        }
    }
    
    palabras_accion = ["crear", "registrar", "hacer", "nueva", "nuevo", "generar", "agregar"]
    
    for palabras_clave, accion in acciones_mapa.items():
        for palabra_clave in palabras_clave:
            if palabra_clave in pregunta_lower:
                if any(acc in pregunta_lower for acc in palabras_accion):
                    return accion
                elif any(frase in pregunta_lower for frase in ["ayud", "cómo", "paso", "quiero", "necesito", "dime"]):
                    return accion

    if any(word in pregunta_lower for word in ["ayud", "cómo", "paso", "quiero", "necesito"]) and any(word in pregunta_lower for word in palabras_accion):
        return {
            "tipo": "consulta_ayuda",
            "entidad": "general",
            "instrucciones": "Por favor, sé más específico. ¿Qué deseas crear o registrar? Algunas opciones: talle, orden, entrada de tela, producto terminado, remisión, colilla"
        }

    return None


def procesar_pregunta(pregunta: str, db: Session, contexto: str = "general") -> RespuestaChat:
    """Procesa la pregunta y genera respuesta con informe contextual"""

    # Primero, detectar si es una solicitud de ayuda para una acción
    intencion = detectar_intencion_accion(pregunta)
    
    if intencion:
        # Es una solicitud de ayuda para una acción
        respuesta_texto = f"""
**{intencion.get('titulo', 'Ayuda')}**

{intencion.get('instrucciones', '')}

📝 **Pasos a seguir:**
"""
        if intencion.get("pasos"):
            respuesta_texto += "\n".join(intencion["pasos"])
        
        # Solo crear acciones si tenemos destino y pasos específicos
        acciones_list = []
        if intencion.get("destino") and intencion.get("pasos"):
            accion_obj = Accion(
                tipo=intencion.get("tipo", "instrucciones"),
                titulo=intencion.get("titulo", "Ayuda"),
                descripcion=intencion.get("instrucciones", ""),
                entidad=intencion.get("entidad"),
                destino=intencion.get("destino"),
                pasos=intencion.get("pasos"),
                payload=intencion.get("payload")
            )
            acciones_list = [accion_obj.model_dump(exclude_none=True)]
        
        return RespuestaChat(
            pregunta=pregunta,
            respuesta=respuesta_texto,
            tipo="ayuda_accion",
            informe_detallado=intencion,
            acciones=acciones_list,
            sugerencias=generar_sugerencias_seguimiento('ayuda_accion', contexto)
        )
    
    # Si no es una acción, continuar con análisis normal
    pregunta_lower = pregunta.lower()

    # Si el contexto es específico, priorizar análisis contextual
    if contexto == "bodega":
        tipo = "inventario"
        informe = generar_informe_inventario(db)
        respuesta = f"""
**Análisis de Bodega**

En la sección de Bodega, el enfoque principal es la gestión de inventario de productos terminados.

📦 **Estado Actual del Inventario:**
- Total de productos: {informe.get('total_productos', 0)}
- Stock total: {informe.get('stock_total', 0)} unidades
- Valor del inventario: ${informe.get('valor_inventario', 0)}
- Productos bajo stock: {informe.get('productos_bajo_stock', 0)}

⚠️ **Punto de Reorden:**
- Recomendado: {informe.get('punto_reorden_recomendado', 0)} unidades

✅ **Acciones Recomendadas para Bodega:**
{chr(10).join(f"• {rec}" for rec in informe.get('recomendaciones', []))}
        """

    elif contexto == "inventario_tela":
        tipo = "inventario"
        informe = generar_informe_inventario(db)
        respuesta = f"""
**Análisis de Inventario de Tela**

En la sección de Inventario de Tela, se gestiona el stock de materias primas.

📊 **Gestión de Tela:**
- Productos disponibles: {informe.get('total_productos', 0)}
- Stock total: {informe.get('stock_total', 0)} unidades
- Valor en stock: ${informe.get('valor_inventario', 0)}

🔄 **Disponibilidad:**
- Productos en buen nivel: {informe.get('total_productos', 0) - informe.get('productos_bajo_stock', 0)}
- Productos bajo stock: {informe.get('productos_bajo_stock', 0)}

📌 **Próximas Acciones:**
{chr(10).join(f"• {rec}" for rec in informe.get('recomendaciones', []))}
        """

    elif contexto == "lotes_produccion":
        tipo = "demanda"
        informe = generar_informe_demanda(db)
        respuesta = f"""
**Análisis de Lotes de Producción**

En esta sección se gestionan los lotes de producción y demanda.

📋 **Lotes Registrados (últimos 30 días):**
- Total de lotes: {informe.get('total_lotes', 0)}
- Cantidad promedio por lote: {informe.get('cantidad_promedio', 0)} unidades/día
- Cantidad total producida: {informe.get('cantidad_total', 0)} unidades

📈 **Predicción de Demanda (Próximos 7 días):**
{json.dumps(informe.get('predicciones_7_dias', []), indent=2, ensure_ascii=False)}

✅ **Recomendaciones de Producción:**
{chr(10).join(f"• {rec}" for rec in informe.get('recomendaciones', []))}
        """

    elif contexto == "calidad" or contexto == "colillas":
        tipo = "calidad"
        informe = generar_informe_calidad(db)
        respuesta = f"""
**Análisis de Control de Calidad**

En esta sección se registra y monitorea la calidad de los productos.

🔍 **Inspecciones (últimos 30 días):**
- Total de inspecciones: {informe.get('total_inspecciones', 0)}
- Prendas defectuosas: {informe.get('prendas_defectuosas', 0)}
- Tasa de defectos: {informe.get('tasa_defectos_porcentaje', 0)}%
- Tasa de conformidad: {informe.get('tasa_conformidad', 0)}%

⚠️ **Estado de Calidad: {informe.get('estado', 'Desconocido')}**

🎯 **Anomalías Detectadas:** {informe.get('anomalias_detectadas', 0)}

✅ **Acciones para Mejorar Calidad:**
{chr(10).join(f"• {rec}" for rec in informe.get('recomendaciones', []))}
        """

    elif contexto == "producto_terminado":
        tipo = "inventario"
        informe = generar_informe_inventario(db)
        respuesta = f"""
**Análisis de Productos Terminados**

Gestión y seguimiento de productos listos para distribución.

✨ **Productos Terminados en Stock:**
- Total de tipos: {informe.get('total_productos', 0)}
- Unidades totales: {informe.get('stock_total', 0)}
- Valor total: ${informe.get('valor_inventario', 0)}
- Listos para distribuir: {informe.get('total_productos', 0) - informe.get('productos_bajo_stock', 0)}

📉 **Necesita Reposición:** {informe.get('productos_bajo_stock', 0)} tipos

✅ **Recomendaciones para Distribución:**
{chr(10).join(f"• {rec}" for rec in informe.get('recomendaciones', []))}
        """

    elif contexto == "dashboard":
        tipo = "general"
        demanda = generar_informe_demanda(db)
        calidad = generar_informe_calidad(db)
        inventario = generar_informe_inventario(db)

        respuesta = f"""
**📊 Resumen General del Dashboard**

**Demanda y Producción:**
- Total de lotes (30 días): {demanda.get('total_lotes', 0)}
- Cantidad promedio: {demanda.get('cantidad_promedio', 0)} unidades/día
- Predicción próximos 7 días: {len(demanda.get('predicciones_7_dias', []))} pronósticos

**Control de Calidad:**
- Tasa de defectos: {calidad.get('tasa_defectos_porcentaje', 0)}%
- Estado: {calidad.get('estado', 'Desconocido')}
- Anomalías: {calidad.get('anomalias_detectadas', 0)}

**Inventario General:**
- Stock total: {inventario.get('stock_total', 0)} unidades
- Valor: ${inventario.get('valor_inventario', 0)}
- Punto de reorden: {inventario.get('punto_reorden_recomendado', 0)} unidades

🎯 **Principales Acciones Recomendadas:**
{chr(10).join(f"• {rec}" for rec in demanda.get('recomendaciones', [])[:1])}
{chr(10).join(f"• {rec}" for rec in calidad.get('recomendaciones', [])[:1])}
{chr(10).join(f"• {rec}" for rec in inventario.get('recomendaciones', [])[:1])}
        """

        informe = {
            "demanda": demanda,
            "calidad": calidad,
            "inventario": inventario
        }

    # Si no hay contexto específico, detectar por palabras clave
    elif any(word in pregunta_lower for word in ["demanda", "venta", "producción", "lotes", "cuánto"]):
        tipo = "demanda"
        informe = generar_informe_demanda(db)
        respuesta = f"""
**Informe de Demanda**

Período: {informe.get('periodo', 'N/A')}

📊 **Datos Principales:**
- Total de lotes: {informe.get('total_lotes', 0)}
- Cantidad promedio: {informe.get('cantidad_promedio', 0)} unidades/día
- Cantidad total producida: {informe.get('cantidad_total', 0)} unidades
- Variabilidad: {informe.get('variabilidad', 'N/A')} unidades

📈 **Predicciones (Próximos 7 días):**
{json.dumps(informe.get('predicciones_7_dias', []), indent=2, ensure_ascii=False)}

✅ **Recomendaciones:**
{chr(10).join(f"• {rec}" for rec in informe.get('recomendaciones', []))}
        """

    elif any(word in pregunta_lower for word in ["calidad", "defecto", "anomalía", "inspección", "conformidad"]):
        tipo = "calidad"
        informe = generar_informe_calidad(db)
        respuesta = f"""
**Informe de Calidad**

Período: {informe.get('periodo', 'N/A')}

🔍 **Datos Principales:**
- Total de inspecciones: {informe.get('total_inspecciones', 0)}
- Prendas defectuosas: {informe.get('prendas_defectuosas', 0)}
- Tasa de defectos: {informe.get('tasa_defectos_porcentaje', 0)}%
- Tasa de conformidad: {informe.get('tasa_conformidad', 0)}%
- Anomalías detectadas: {informe.get('anomalias_detectadas', 0)}
- **Estado: {informe.get('estado', 'Desconocido')}**

✅ **Recomendaciones:**
{chr(10).join(f"• {rec}" for rec in informe.get('recomendaciones', []))}
        """

    elif any(word in pregunta_lower for word in ["inventario", "stock", "almacén", "producto", "reorden"]):
        tipo = "inventario"
        informe = generar_informe_inventario(db)
        respuesta = f"""
**Informe de Inventario**

📦 **Datos Principales:**
- Total de productos: {informe.get('total_productos', 0)}
- Stock total: {informe.get('stock_total', 0)} unidades
- Valor del inventario: ${informe.get('valor_inventario', 0)}
- Productos bajo stock: {informe.get('productos_bajo_stock', 0)}
- Punto de reorden recomendado: {informe.get('punto_reorden_recomendado', 0)} unidades

📊 **Métricas:**
- Rotación: {informe.get('rotacion_inventario', 'N/A')}

✅ **Recomendaciones:**
{chr(10).join(f"• {rec}" for rec in informe.get('recomendaciones', []))}
        """

    else:
        tipo = "general"
        demanda = generar_informe_demanda(db)
        calidad = generar_informe_calidad(db)
        inventario = generar_informe_inventario(db)

        respuesta = f"""
**Análisis General del Sistema**

📊 **Resumen Ejecutivo:**

**Demanda:**
- Total de lotes (30 días): {demanda.get('total_lotes', 0)}
- Cantidad promedio: {demanda.get('cantidad_promedio', 0)} unidades/día

**Calidad:**
- Tasa de defectos: {calidad.get('tasa_defectos_porcentaje', 0)}%
- Estado: {calidad.get('estado', 'Desconocido')}

**Inventario:**
- Stock total: {inventario.get('stock_total', 0)} unidades
- Valor: ${inventario.get('valor_inventario', 0)}

🎯 **Recomendaciones Generales:**
{chr(10).join(f"• {rec}" for rec in demanda.get('recomendaciones', []))}
{chr(10).join(f"• {rec}" for rec in calidad.get('recomendaciones', []))}
{chr(10).join(f"• {rec}" for rec in inventario.get('recomendaciones', []))}
        """

        informe = {
            "demanda": demanda,
            "calidad": calidad,
            "inventario": inventario
        }

    return RespuestaChat(
        pregunta=pregunta,
        respuesta=respuesta.strip(),
        tipo=tipo,
        informe_detallado=informe,
        acciones=obtener_acciones_recomendadas(tipo, contexto),
        sugerencias=generar_sugerencias_seguimiento(tipo, contexto)
    )


from pydantic import ValidationError


def ejecutar_accion_backend(accion: AccionRequest, db: Session) -> dict:
    """Ejecuta una acción concreta usando endpoints internos conocidos."""
    entidad = accion.entidad or (accion.payload and accion.payload.get('entidad'))
    datos = None
    if accion.payload:
        if isinstance(accion.payload, dict) and 'data' in accion.payload:
            datos = accion.payload.get('data')
        else:
            datos = accion.payload

    def campos_faltantes(datos: dict, requeridos: list) -> list:
        return [campo for campo in requeridos if datos.get(campo) in (None, '', [])]

    try:
        def resolver_material_y_color(datos: dict) -> dict:
            from app.models import Material, Color

            if not datos.get('material_id') and datos.get('material_nombre'):
                material_nombre = str(datos.get('material_nombre')).strip()
                material = db.query(Material).filter(Material.nombre == material_nombre).first()
                if not material:
                    material = Material(codigo=material_nombre.upper().replace(' ', '-')[:20], nombre=material_nombre, activo=True)
                    db.add(material)
                    db.flush()
                datos['material_id'] = int(material.id)

            if not datos.get('color_id') and datos.get('color_nombre'):
                color_nombre = str(datos.get('color_nombre')).strip()
                color = db.query(Color).filter(Color.nombre == color_nombre).first()
                if not color:
                    color = Color(codigo=color_nombre.upper().replace(' ', '-')[:20], nombre=color_nombre, activo=True)
                    db.add(color)
                    db.flush()
                datos['color_id'] = int(color.id)

            return datos

        if entidad == 'tela':
            datos = resolver_material_y_color(datos or {})
            if not datos or campos_faltantes(datos, ['material_id', 'color_id', 'cantidad', 'lote_proveedor']):
                faltan = campos_faltantes(datos or {}, ['material_id', 'color_id', 'cantidad', 'lote_proveedor'])
                return {
                    'exitoso': False,
                    'mensaje': f"Faltan datos para registrar tela. Se requieren: {', '.join(faltan)}.",
                    'faltan_campos': faltan,
                    'payload': accion.payload
                }
            if datos.get('cantidad') is not None and datos.get('cantidad') <= 0:
                return {
                    'exitoso': False,
                    'mensaje': 'La cantidad de tela debe ser mayor que cero.',
                    'faltan_campos': ['cantidad'],
                    'payload': accion.payload
                }
            from app.api.inventario_tela import ingresar_rollos
            ingreso = IngresoRolloCreate(**datos)
            movimiento = ingresar_rollos(ingreso, db)
            return {
                'exitoso': True,
                'mensaje': 'Entrada de tela registrada con éxito',
                'payload': movimiento
            }

        if entidad == 'orden':
            if not datos:
                return {
                    'exitoso': False,
                    'mensaje': 'Faltan datos para crear la orden de producción. Proporciona el lote completo.',
                    'payload': accion.payload
                }
            faltan = campos_faltantes(datos, ['numero_lote', 'referencia_nombre', 'material_nombre', 'fecha_corte', 'detalles'])
            if faltan:
                return {
                    'exitoso': False,
                    'mensaje': f"Faltan datos para crear la orden de producción. Se requieren: {', '.join(faltan)}.",
                    'faltan_campos': faltan,
                    'payload': accion.payload
                }
            detalles = datos.get('detalles') or []
            if not isinstance(detalles, list) or len(detalles) == 0:
                return {
                    'exitoso': False,
                    'mensaje': 'La orden de producción requiere al menos un detalle con color_nombre, talla_id y cantidad.',
                    'faltan_campos': ['detalles'],
                    'payload': accion.payload
                }
            from app.api.lotes_produccion import crear_lote
            lote = LoteCreate(**datos)
            resultado = crear_lote(lote, db)
            return {
                'exitoso': True,
                'mensaje': 'Orden de producción creada con éxito',
                'payload': resultado
            }

        if entidad == 'remisión':
            if not datos:
                return {
                    'exitoso': False,
                    'mensaje': 'Faltan datos para crear la remisión. Proporciona el número de remisión, lote_id, taller_id y detalles.',
                    'payload': accion.payload
                }
            faltan = campos_faltantes(datos, ['numero_remision', 'lote_id', 'taller_id', 'fecha_remision', 'detalles'])
            if faltan:
                return {
                    'exitoso': False,
                    'mensaje': f"Faltan datos para crear la remisión. Se requieren: {', '.join(faltan)}.",
                    'faltan_campos': faltan,
                    'payload': accion.payload
                }
            detalles = datos.get('detalles') or []
            if not isinstance(detalles, list) or len(detalles) == 0:
                return {
                    'exitoso': False,
                    'mensaje': 'La remisión requiere al menos un detalle con talla_id y cantidad.',
                    'faltan_campos': ['detalles'],
                    'payload': accion.payload
                }
            from app.api.taller import crear_remision
            remision = RemisionCreate(**datos)
            resultado = crear_remision(remision, db)
            return {
                'exitoso': True,
                'mensaje': 'Remisión creada con éxito',
                'payload': resultado
            }

        if entidad == 'talle':
            if not datos or campos_faltantes(datos, ['codigo', 'nombre']):
                faltan = campos_faltantes(datos or {}, ['codigo', 'nombre'])
                return {
                    'exitoso': False,
                    'mensaje': f"Faltan datos para crear el taller. Se requieren: {', '.join(faltan)}.",
                    'faltan_campos': faltan,
                    'payload': accion.payload
                }
            from app.api.taller import crear_taller
            taller = TallerCreate(**datos)
            resultado = crear_taller(taller, db)
            return {
                'exitoso': True,
                'mensaje': 'Taller creado con éxito',
                'payload': resultado
            }

        def resolver_lote_y_taller(datos: dict) -> dict:
            from app.models import Lote, Taller

            if not datos.get('lote_id') and datos.get('lote_numero'):
                lote_numero = str(datos.get('lote_numero')).strip()
                lote = db.query(Lote).filter(Lote.numero_lote == lote_numero).first()
                if lote:
                    datos['lote_id'] = int(lote.id)

            if not datos.get('taller_id') and datos.get('taller_nombre'):
                taller_nombre = str(datos.get('taller_nombre')).strip()
                taller = db.query(Taller).filter(Taller.nombre == taller_nombre).first()
                if taller:
                    datos['taller_id'] = int(taller.id)

            return datos

        def resolver_talla_y_color(datos: dict) -> dict:
            from app.models import Talla, Color

            if not datos.get('talla_id') and datos.get('talla_nombre'):
                talla_nombre = str(datos.get('talla_nombre')).strip()
                talla = db.query(Talla).filter(Talla.nombre == talla_nombre).first()
                if not talla:
                    codigo_talla = talla_nombre.upper().replace(' ', '-')[:10]
                    talla = Talla(codigo=codigo_talla, nombre=talla_nombre, activo=True)
                    db.add(talla)
                    db.flush()
                datos['talla_id'] = int(talla.id)

            if not datos.get('color_id') and datos.get('color_nombre'):
                color_nombre = str(datos.get('color_nombre')).strip()
                color = db.query(Color).filter(Color.nombre == color_nombre).first()
                if not color:
                    color = Color(codigo=color_nombre.upper().replace(' ', '-')[:20], nombre=color_nombre, activo=True)
                    db.add(color)
                    db.flush()
                datos['color_id'] = int(color.id)

            return datos

        if entidad == 'colilla':
            datos = resolver_lote_y_taller(datos or {})
            if not datos:
                return {
                    'exitoso': False,
                    'mensaje': 'Faltan datos para registrar la colilla. Proporciona lote_id, taller_id, confeccionista_nombre y demás detalles.',
                    'payload': accion.payload
                }
            faltan = campos_faltantes(datos, ['lote_id', 'taller_id', 'confeccionista_nombre', 'tipo_trabajo', 'cantidad_prendas'])
            if faltan:
                return {
                    'exitoso': False,
                    'mensaje': f"Faltan datos para registrar la colilla. Se requieren: {', '.join(faltan)}.",
                    'faltan_campos': faltan,
                    'payload': accion.payload
                }
            from app.api.colillas import crear_colilla
            colilla = ColillaCreate(**datos)
            resultado = crear_colilla(colilla, db)
            return {
                'exitoso': True,
                'mensaje': 'Colilla creada con éxito',
                'payload': resultado
            }

        if entidad == 'remisión':
            datos = resolver_lote_y_taller(datos or {})
            if not datos:
                return {
                    'exitoso': False,
                    'mensaje': 'Faltan datos para crear la remisión. Proporciona el número de remisión, lote_id, taller_id y detalles.',
                    'payload': accion.payload
                }
            faltan = campos_faltantes(datos, ['numero_remision', 'lote_id', 'taller_id', 'fecha_remision', 'detalles'])
            if faltan:
                return {
                    'exitoso': False,
                    'mensaje': f"Faltan datos para crear la remisión. Se requieren: {', '.join(faltan)}.",
                    'faltan_campos': faltan,
                    'payload': accion.payload
                }
            detalles = datos.get('detalles') or []
            if not isinstance(detalles, list) or len(detalles) == 0:
                return {
                    'exitoso': False,
                    'mensaje': 'La remisión requiere al menos un detalle con talla_id y cantidad.',
                    'faltan_campos': ['detalles'],
                    'payload': accion.payload
                }
            from app.api.taller import crear_remision
            remision = RemisionCreate(**datos)
            resultado = crear_remision(remision, db)
            return {
                'exitoso': True,
                'mensaje': 'Remisión creada con éxito',
                'payload': resultado
            }

        if entidad in ('producto', 'producto_terminado'):
            datos = resolver_talla_y_color(datos or {})
            if not datos:
                return {
                    'exitoso': False,
                    'mensaje': 'Faltan datos para registrar producto terminado. Proporciona SKU, tipo, talla_id, color_id, zona y cantidad_actual.',
                    'payload': accion.payload
                }
            faltan = campos_faltantes(datos, ['sku', 'tipo', 'talla_id', 'color_id', 'zona', 'cantidad_actual'])
            if faltan:
                return {
                    'exitoso': False,
                    'mensaje': f"Faltan datos para registrar producto terminado. Se requieren: {', '.join(faltan)}.",
                    'faltan_campos': faltan,
                    'payload': accion.payload
                }
            from app.api.inventario_pt import ingresar_stock
            ingreso = ProductoTerminadoStockCreate(**datos)
            resultado = ingresar_stock(ingreso, db)
            return {
                'exitoso': True,
                'mensaje': 'Producto terminado registrado con éxito',
                'payload': resultado
            }

        return {
            'exitoso': False,
            'mensaje': 'No se encontró una acción ejecutable con los datos proporcionados. Por favor completa los campos necesarios para ejecutar la acción.',
            'payload': accion.payload
        }
    except ValidationError as err:
        return {
            'exitoso': False,
            'mensaje': f'Datos inválidos para la acción: {err}',
            'payload': accion.payload
        }


@router.post("/accion")
async def ejecutar_accion(accion: AccionRequest, db: Session = Depends(get_db)):
    """Endpoint para ejecutar acciones definidas por el asistente IA."""
    try:
        resultado = ejecutar_accion_backend(accion, db)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def chat_ia(request: PreguntaChat, db: Session = Depends(get_db)):
    """
    Endpoint de chat con IA. Acepta preguntas en lenguaje natural
    y retorna informes detallados contextualizados.

    Ejemplos de preguntas:
    - "¿Cuál es la demanda esperada?"
    - "¿Cómo está la calidad?"
    - "¿Cuánto stock tenemos?"
    - "Dame un análisis general del sistema"

    Contextos soportados:
    - bodega: Análisis de inventario de bodega
    - inventario_tela: Análisis de tela disponible
    - lotes_produccion: Análisis de lotes
    - calidad/colillas: Análisis de calidad
    - producto_terminado: Análisis de productos terminados
    - dashboard: Análisis general del sistema
    """
    try:
        if not request.pregunta or len(request.pregunta.strip()) == 0:
            raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía")

        respuesta = procesar_pregunta(request.pregunta, db, request.contexto)
        return respuesta

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/sugerencias")
async def obtener_sugerencias(contexto: str = "general"):
    """Retorna sugerencias de preguntas contextualizadas según la sección actual"""
    
    # Sugerencias contextuales por sección
    sugerencias_por_contexto = {
        "bodega": [
            "¿Cuál es el stock disponible en bodega?",
            "¿Hay productos bajo stock?",
            "¿Cuánto vale el inventario?",
            "¿Necesitamos hacer pedidos?",
            "¿Cuál es el punto de reorden?",
            "¿Cuántos tipos de productos tenemos?"
        ],
        "inventario_tela": [
            "¿Cuánta tela está disponible?",
            "¿Hay tela bajo stock?",
            "¿Cuál es el valor del inventario de tela?",
            "¿Qué materiales necesitan reorden?",
            "¿Cuál es el punto de reorden para tela?"
        ],
        "lotes_produccion": [
            "¿Cuál es la demanda esperada?",
            "¿Cuántos lotes se han producido?",
            "¿Cuál es la cantidad promedio por lote?",
            "¿Cuál es la predicción para los próximos 7 días?",
            "¿Necesitamos aumentar la producción?"
        ],
        "calidad": [
            "¿Cómo está el control de calidad?",
            "¿Cuántas prendas defectuosas hemos detectado?",
            "¿Cuál es la tasa de defectos?",
            "¿Hay anomalías detectadas?",
            "¿Cuál es la tasa de conformidad?"
        ],
        "colillas": [
            "¿Cuál es el estado de calidad?",
            "¿Hay anomalías en la producción?",
            "¿Cuál es la tasa de defectos?",
            "¿Cuántas prendas se inspeccionaron?"
        ],
        "producto_terminado": [
            "¿Cuántos productos terminados hay?",
            "¿Hay productos listos para distribuir?",
            "¿Cuál es el valor de productos terminados?",
            "¿Necesitamos más producción?",
            "¿Cuántos tipos de productos están disponibles?"
        ],
        "dashboard": [
            "¿Cuál es el estado general del sistema?",
            "¿Cómo está la demanda?",
            "¿Cómo está la calidad?",
            "¿Cuál es el estado del inventario?",
            "Dame un resumen ejecutivo"
        ]
    }
    
    # Retornar sugerencias del contexto o generales
    if contexto in sugerencias_por_contexto:
        return {"sugerencias": sugerencias_por_contexto[contexto]}
    
    return {
        "sugerencias": [
            "¿Cuál es la demanda esperada para los próximos 7 días?",
            "¿Cómo está el control de calidad?",
            "¿Cuánto stock tenemos disponible?",
            "¿Cuál es el punto de reorden recomendado?",
            "Dame un análisis general del sistema",
            "¿Hay anomalías detectadas en la producción?",
            "¿Cuántas prendas defectuosas hemos detectado?",
            "¿Cuál es el valor total del inventario?"
        ]
    }
