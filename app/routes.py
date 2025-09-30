from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas
import crud
import auth
from core.deps import get_db

router = APIRouter()

@router.post("/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = crud.create_user(db, user.username, user.password)
    token = auth.create_access_token({"sub": new_user.username})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.authenticate_user(db, user.username, user.password)
    token = auth.create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/users", response_model=List[schemas.User])
def list_users(db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return users
