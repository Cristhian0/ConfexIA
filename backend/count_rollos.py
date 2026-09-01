from app.db.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM rollo_stocks'))
    count = result.fetchone()[0]
    print("Count in rollo_stocks:", count)