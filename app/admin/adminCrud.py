from sqlalchemy.orm import Session
from fastapi import HTTPException

from . import adminModels, adminAuth

def get_user_by_username(db: Session, username: str):
    return db.query(adminModels.User).filter(adminModels.User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not adminAuth.verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

def create_user(db: Session, username: str, password: str):
    hashed_password = adminAuth.hash_password(password)
    new_user = adminModels.User(username=username, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# -------------------------
# Додаємо функцію для списку користувачів
def get_users(db: Session):
    return db.query(adminModels.User).all()
