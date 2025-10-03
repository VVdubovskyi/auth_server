from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

SECRET_KEY = "supersecretkey"  # замінити на os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, db: Session = None, expires_delta: timedelta | None = None):
    """Створює JWT токен та зберігає його в БД"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # Зберігаємо токен в БД, якщо передано db session
    if db and "admin_id" in data:
        from . import userModels

        session = userModels.UserSession(
            user_id=data["user_id"],
            token=token,
            expires_at=expire,
            is_active= True
        )
        db.add(session)
        db.commit()

    return token


def decode_access_token(token: str):
    """Декодує JWT токен та повертає payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token_in_db(token: str, db: Session):
    """Перевіряє, чи токен активний в БД"""
    from . import userModels

    session = db.query(userModels.UserSession).filter(
        userModels.UserSession.token == token,
        userModels.UserSession.is_active == True,
        userModels.UserSession.expires_at > datetime.utcnow()
    ).first()

    return session is not None


def invalidate_token(token: str, db: Session):
    """Деактивує токен в БД (logout)"""
    from . import userModels

    session = db.query(userModels.UserSession).filter(
        userModels.UserSession.token == token
    ).first()

    if session:
        session.is_active = False
        db.commit()
        return True
    return False