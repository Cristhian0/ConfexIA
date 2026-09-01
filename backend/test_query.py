from app.db.database import get_db
from sqlalchemy.orm import Session
from app.models import Material, Color
from app.models.bodega import RolloStock

db: Session = next(get_db())

try:
    items = (
        db.query(RolloStock, Material.nombre.label("material_nombre"), Color.nombre.label("color_nombre"))
        .join(Material, Material.id == RolloStock.material_id)
        .join(Color, Color.id == RolloStock.color_id)
        .order_by(RolloStock.id.desc())
        .all()
    )
    print("Query successful, items:", len(items))
    for stock, mat, col in items[:5]:  # first 5
        print(f"Stock: {stock.id}, Mat: {mat}, Col: {col}")
except Exception as e:
    print("Error:", e)