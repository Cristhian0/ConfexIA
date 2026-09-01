import sys
sys.path.insert(0, 'backend')
from app.db.database import SessionLocal
from app.api.dashboard import obtener_detalle_colores_tallas

session = SessionLocal()
try:
    result = obtener_detalle_colores_tallas(session)
    print('ok', len(result))
except Exception:
    import traceback
    traceback.print_exc()
finally:
    session.close()
