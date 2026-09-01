"""
Script para generar datos de prueba y entrenar modelos de IA
Crea datos sintéticos realistas para demostración
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
import random
import numpy as np

# Agregar el backend al path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.models.lote import Lote
from app.models.colilla import Colilla
from app.core.ml_models import (
    predictor_demanda,
    detector_defectos,
    recomendador_inventario
)


def generar_datos_demanda(db: Session, dias=60):
    """Genera datos sintéticos de demanda"""
    print(f"📊 Generando {dias} días de datos de demanda...")
    
    for i in range(dias, 0, -1):
        fecha = datetime.now() - timedelta(days=i)
        # Simular demanda con tendencia y variación estacional
        cantidad_base = 150
        variacion = np.random.randint(-30, 50)
        cantidad = max(50, cantidad_base + variacion)
        
        lote = Lote(
            cantidad=cantidad,
            estado="completado",
            descripcion=f"Lote de demostración {i}",
            fecha_creacion=fecha
        )
        db.add(lote)
    
    db.commit()
    print(f"✅ {dias} registros de demanda creados")


def generar_datos_defectos(db: Session, cantidad=100):
    """Genera datos sintéticos de defectos"""
    print(f"📋 Generando {cantidad} registros de calidad...")
    
    for i in range(cantidad):
        # 80% sin defectos, 20% con defectos
        tiene_defecto = random.random() < 0.2
        
        colilla = Colilla(
            defecto=f"Defecto tipo A - Lote {i}" if tiene_defecto else None,
            descripcion=f"Registro de calidad #{i}",
            estado="procesada"
        )
        db.add(colilla)
    
    db.commit()
    print(f"✅ {cantidad} registros de calidad creados")


def entrenar_modelos():
    """Entrena todos los modelos de IA"""
    print("\n🤖 Entrenando modelos de IA...")
    
    db = SessionLocal()
    
    try:
        # 1. Entrenar predictor de demanda
        print("\n1️⃣ Entrenando predictor de demanda...")
        lotes = db.query(Lote).all()
        
        datos_historicos = []
        for lote in lotes:
            if lote.fecha_creacion and lote.cantidad:
                datos_historicos.append({
                    'fecha': lote.fecha_creacion.isoformat(),
                    'cantidad': int(lote.cantidad)
                })
        
        if len(datos_historicos) > 10:
            exito = predictor_demanda.entrenar(datos_historicos)
            print(f"   ✅ Predictor de demanda: {'Entrenado' if exito else 'Sin entrenar'}")
            print(f"   📈 Registros usados: {len(datos_historicos)}")
        
        # 2. Entrenar detector de defectos
        print("\n2️⃣ Entrenando detector de defectos...")
        colillas = db.query(Colilla).all()
        
        datos_defectos = []
        for colilla in colillas:
            datos_defectos.append({
                'cantidad_defectos': 1 if colilla.defecto else 0,
                'porcentaje_rechazo': 10.0 if colilla.defecto else 0.0,
                'horas_produccion': 8.0
            })
        
        if len(datos_defectos) > 20:
            exito = detector_defectos.entrenar(datos_defectos)
            print(f"   ✅ Detector de defectos: {'Entrenado' if exito else 'Sin entrenar'}")
            print(f"   📊 Registros usados: {len(datos_defectos)}")
        
        # 3. Mostrar ejemplo de recomendación
        print("\n3️⃣ Calculando recomendaciones de inventario...")
        
        # Calcular demanda promedio
        cantidades = [lote.cantidad for lote in lotes if lote.cantidad]
        if cantidades:
            demanda_promedio = np.mean(cantidades)
            desv_std = np.std(cantidades)
            
            punto_reorden = recomendador_inventario.calcular_punto_reorden(
                demanda_promedio=demanda_promedio,
                lead_time_dias=5,
                desviacion_estandar=desv_std
            )
            
            print(f"   📍 Punto de reorden: {punto_reorden['punto_reorden']}")
            print(f"   🔒 Stock de seguridad: {punto_reorden['stock_seguridad']}")
            print(f"   💡 Recomendación: {punto_reorden['recomendacion']}")
        
        print("\n" + "="*60)
        print("✅ ENTRENAMIENTO COMPLETADO")
        print("="*60)
        print("\n📌 Modelos disponibles:")
        print(f"   • Predictor de demanda: {'✅ Listo' if predictor_demanda.entrenado else '❌ No disponible'}")
        print(f"   • Detector de defectos: {'✅ Listo' if detector_defectos.entrenado else '❌ No disponible'}")
        print(f"   • Recomendador de inventario: ✅ Siempre disponible")
        
        print("\n🔗 Endpoints disponibles en la API:")
        print("   POST   /api/v1/predicciones/entrenar/demanda")
        print("   GET    /api/v1/predicciones/demanda?dias=7")
        print("   POST   /api/v1/predicciones/entrenar/defectos")
        print("   POST   /api/v1/predicciones/defectos/detectar")
        print("   POST   /api/v1/predicciones/inventario/punto-reorden")
        print("   POST   /api/v1/predicciones/inventario/cantidad-economica")
        print("   GET    /api/v1/predicciones/dashboard/insights")
        
    finally:
        db.close()


def limpiar_datos(db: Session):
    """Limpia datos de prueba"""
    print("\n🗑️  Limpiando datos previos...")
    db.query(Lote).delete()
    db.query(Colilla).delete()
    db.commit()
    print("   ✅ Datos limpios")


if __name__ == "__main__":
    db = SessionLocal()
    
    print("\n" + "="*60)
    print("🚀 GENERADOR DE DATOS DE PRUEBA - IA")
    print("="*60)
    
    try:
        # Limpiar datos previos
        limpiar_datos(db)
        
        # Generar datos
        generar_datos_demanda(db, dias=60)
        generar_datos_defectos(db, cantidad=100)
        
        # Entrenar modelos
        entrenar_modelos()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()
