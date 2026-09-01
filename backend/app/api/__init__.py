from fastapi import APIRouter
from app.api import catalogo, lotes_produccion, taller, confeccion, control_calidad, dashboard, importacion, documentos, inventario_tela, inventario_pt, corte, produccion, calidad, bodega, colillas, auth, predicciones, chat_ia

router = APIRouter()

router.include_router(catalogo.router, prefix="/catalogo", tags=["Catálogo"])
router.include_router(lotes_produccion.router, prefix="/lotes-produccion", tags=["Lotes de Producción"])
router.include_router(taller.router, prefix="/talleres", tags=["Talleres"])
router.include_router(confeccion.router, prefix="/confeccion", tags=["Confección"])
router.include_router(produccion.router, prefix="/produccion", tags=["Producción"])
router.include_router(calidad.router, prefix="/calidad", tags=["Control de Calidad - RF-15-18"])
router.include_router(control_calidad.router, prefix="/control-calidad", tags=["Control de Calidad"])
router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(importacion.router, prefix="/importacion", tags=["Importación"])
router.include_router(documentos.router, prefix="/documentos", tags=["Documentos"])
router.include_router(inventario_tela.router, prefix="/inventario-tela", tags=["Inventario de Tela"])
router.include_router(inventario_pt.router, prefix="/inventario-pt", tags=["Inventario Producto Terminado"])
router.include_router(bodega.router, prefix="/bodega", tags=["Bodega"])
router.include_router(corte.router, prefix="/corte", tags=["Corte"])
router.include_router(colillas.router, prefix="/colillas", tags=["Colillas"])
router.include_router(predicciones.router, prefix="/predicciones", tags=["IA y Predicciones"])
router.include_router(chat_ia.router, prefix="/chat", tags=["Chat IA"])


