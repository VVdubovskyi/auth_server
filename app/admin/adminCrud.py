from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional, List

from . import adminModels, adminAuth, adminSchemas
from users import userModels
from .adminModels import AdminSession


# ============= АДМІНІСТРАТОРИ =============
def get_admin_by_username(db: Session, username: str):
    return db.query(adminModels.Admin).filter(adminModels.Admin.username == username).first()


def get_admin_by_id(db: Session, user_id: int):
    return db.query(adminModels.Admin).filter(adminModels.Admin.id == user_id).first()


def authenticate_admin(db: Session, username: str, password: str):
    user = get_admin_by_username(db, username)
    if not user or not adminAuth.verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user


def create_admin(db: Session, username: str, password: str, first_name: Optional[str] = None,
                last_name: Optional[str] = None, telegram_id: Optional[str] = None):
    hashed_password = adminAuth.hash_password(password)
    new_user = adminModels.Admin(
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


def get_admins(db: Session):
    return db.query(adminModels.Admin).all()


def get_admin_for_id(db: Session, admin_id: int):
    return db.query(adminModels.Admin).filter(adminModels.Admin.id == admin_id).first()


# ============= УПРАВЛІННЯ ГРУПАМИ КОРИСТУВАЧІВ =============
def assign_managed_user_groups(db: Session, admin_id: int, user_group_ids: List[int]):
    """Призначити адміну групи користувачів, якими він може управляти"""
    admin = get_admin_by_id(db, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    # Перевіряємо, чи існують всі групи користувачів
    user_groups = []
    for group_id in user_group_ids:
        group = db.query(userModels.Group).filter(userModels.Group.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail=f"User group with id {group_id} not found")
        user_groups.append(group)

    # Замінюємо список груп
    admin.managed_user_groups = user_groups
    db.commit()
    db.refresh(admin)
    return admin


def deactivate_token(db: Session, token: str):
    db_token = db.query(AdminSession).filter_by(token=token, is_active=True).first()
    if not db_token:
        return False
    db_token.is_active = False
    db.commit()
    return True


def delete_admin(db: Session, admin_id: int):
    admin = db.query(adminModels.Admin).filter(adminModels.Admin.id == admin_id).first()
    if not admin:
        return None
    db.delete(admin)
    db.commit()
    return admin


def update_admin(db: Session, admin: adminModels.Admin, admin_update: adminSchemas.AdminUpdate):
    update_data = admin_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(admin, key, value)

    db.commit()
    db.refresh(admin)
    return admin



def get_users_for_admin(db: Session, admin_id: int):
    admin = db.query(adminModels.Admin).filter_by(id=admin_id).first()
    if not admin or not admin.group:
        return []
    return admin.group.users