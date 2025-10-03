from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import userSchemas, userCrud, userAuth
from core.deps import get_db
router = APIRouter()

# ============= АУТЕНТИФІКАЦІЯ =============
@router.post(
    "/auth/login",
    response_model=userSchemas.Token,
    summary="Вхід користувача",
    description="Аутентифікує користувача та повертає JWT токен.",
    responses={
        200: {"description": "Успішна аутентифікація"},
        401: {"description": "Невірні облікові дані"}
    }
)
def login(user: userSchemas.UserLogin, db: Session = Depends(get_db)):
    """Аутентифікує користувача за username та паролем.
    
    - **username**: Ім'я користувача
    - **password**: Пароль
    """
    db_user = userCrud.authenticate_user(db, user.username, user.password)
    token = userAuth.create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}

# ============= КОРИСТУВАЧІ =============
# @router.get(
#     "/users-list",
#     response_model=List[userSchemas.User],
#     summary="Список всіх користувачів",
#     description="Повертає список всіх зареєстрованих користувачів у системі."
# )
# def list_users(db: Session = Depends(get_db)):
#     """Отримати повний список користувачів."""
#     users = userCrud.get_users(db)
#     return users
#
# @router.get(
#     "/users/{user_id}",
#     response_model=userSchemas.User,
#     summary="Отримати користувача за ID",
#     description="Повертає детальну інформацію про користувача, включаючи його групу.",
#     responses={
#         200: {"description": "Користувач знайдений"},
#         404: {"description": "Користувач не знайдений"}
#     }
# )
# def get_user(user_id: int, db: Session = Depends(get_db)):
#     """Отримати інформацію про конкретного користувача.
#
#     - **user_id**: ID користувача
#     """
#     user = userCrud.get_user_by_id(db, user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user