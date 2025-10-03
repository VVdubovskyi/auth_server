from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from typing import Optional

from . import userModels, userAuth, userSchemas
from .userSchemas import CreateUsersGroup


# ============= КОРИСТУВАЧІ =============
def get_user_by_username(db: Session, username: str):
    return db.query(userModels.User).filter(userModels.User.username == username).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(userModels.User).filter(userModels.User.id == user_id).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not userAuth.verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user


def create_user(db: Session, username: str, password: str, first_name: Optional[str] = None,
                last_name: Optional[str] = None, telegram_id: Optional[str] = None):
    hashed_password = userAuth.hash_password(password)
    new_user = userModels.User(
        username=username,
        password=hashed_password,
        first_name=first_name,
        last_name=last_name,
        telegram_id=telegram_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_users(db: Session):
    return db.query(userModels.User).all()


def update_user(db: Session, user: userModels.User, user_update: userSchemas.UserUpdate):
    update_data = user_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


def get_group_by_name(db: Session, group_name: str):
    return (
        db.query(userModels.Group)
        .options(joinedload(userModels.Group.users))  # одразу підтягнути користувачів
        .filter(userModels.Group.name == group_name)
        .first()
    )

def create_group(db: Session, name: str, description: str, ):
    new_group = userModels.Group(
        name=name,
        description=description,
    )
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group


def get_groups(db: Session):
    return db.query(userModels.Group).all()
