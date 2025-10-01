from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import adminSchemas, adminCrud, adminAuth
from core.deps import get_db
router = APIRouter()

@router.post("/auth/register", response_model=adminSchemas.Token)
def register(user: adminSchemas.UserCreate, db: Session = Depends(get_db)):
    db_user = adminCrud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = adminCrud.create_user(db, user.username, user.password)
    token = adminAuth.create_access_token({"sub": new_user.username})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/auth/login", response_model=adminSchemas.Token)
def login(user: adminSchemas.UserLogin, db: Session = Depends(get_db)):
    db_user = adminCrud.authenticate_user(db, user.username, user.password)
    token = adminAuth.create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/admins-list", response_model=List[adminSchemas.User])
def list_users(db: Session = Depends(get_db)):
    users = adminCrud.get_users(db)
    return users
