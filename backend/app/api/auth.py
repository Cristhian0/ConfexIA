from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.db.database import get_db, Base, engine
from app.models.user import User
from app.core.security import verify_password, create_access_token, hash_password
from datetime import timedelta

router = APIRouter()


def seed_default_users(db: Session):
    Base.metadata.create_all(bind=engine)
    try:
        existing = db.query(User).count()
        if existing == 0:
            users = [
                {"username": "Admin", "password": "admin123", "role": "admin"},
                {"username": "TallerAD", "password": "Taller123", "role": "taller"},
                {"username": "Dasbo", "password": "dasbo123", "role": "dashboard"},
            ]
            for u in users:
                user = User(username=u["username"], password_hash=hash_password(u["password"]), role=u["role"])
                db.add(user)
            db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


@router.post('/login', response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    username_clean = payload.username.strip()
    seed_default_users(db)
    user = db.query(User).filter(func.lower(User.username) == username_clean.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "role": user.role}
