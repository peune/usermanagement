from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models, schemas
from typing import Any

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()
    
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()
    
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        name=user.name,
        family_name=user.family_name,
        email=user.email,
        workplace=user.workplace,
        position=user.position,
        note=user.note,
        hashed_password=hashed_password,
        is_approved=False,  # New users are not approved by default
        is_superuser=False  # New users are not superuser
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def approve_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        print(db_user, flush=True)
        db_user.is_approved = True
        db.commit()
        db.refresh(db_user)
    return db_user

def reject_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user: return None

    db.delete(db_user)
    db.commit()
    return True