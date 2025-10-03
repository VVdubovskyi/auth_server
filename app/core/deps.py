from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import SessionLocal
from admin import adminAuth, adminCrud

# тут ми вказуємо "фейковий" tokenUrl (Swagger вимагає його для схеми)
# але користуватись ним ти не будеш
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_admin(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    if not adminAuth.verify_token_in_db(token, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен неактивний або прострочений",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = adminAuth.decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний або прострочений токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    admin_id = payload.get("admin_id")
    if admin_id:
        admin = adminCrud.get_admin_by_id(db, admin_id)
        if admin:
            return {"admin": admin, "payload": payload}

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    admin = adminCrud.get_admin_by_username(db, username)
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Адміністратор не знайдений",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"admin": admin, "payload": payload}


def get_current_superadmin(current_admin=Depends(get_current_admin)):
    if not getattr(current_admin, "is_superadmin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ заборонено. Тільки головні адміністратори мають доступ."
        )
    return current_admin
