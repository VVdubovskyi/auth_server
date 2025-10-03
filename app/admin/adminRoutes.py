from typing import List
from fastapi import APIRouter, Depends, HTTPException, Form, status
from sqlalchemy.orm import Session

from users import userCrud, userSchemas, userAuth
from users.userSchemas import ReturnUsersGroup, CreateUsersGroup, UserRead
from . import adminSchemas, adminCrud, adminAuth
from core.deps import get_db, get_current_admin, get_current_superadmin, oauth2_scheme

router = APIRouter()


# --- CREATE (Register) ---
@router.post(
    "/auth/register",
    response_model=adminSchemas.Token,
    summary="Реєстрація адміністратора (тільки для супер-адміна)",
    description="Створює нового адміністратора (тільки для супер-адміна).",
    responses={200: {"description": "Адміністратор успішно зареєстрований"}}
)
def register_admin(admin: adminSchemas.UserCreate, db: Session = Depends(get_db),
                   current_admin=Depends(get_current_superadmin)):
    db_admin = adminCrud.get_admin_by_username(db, admin.username)
    if db_admin:
        raise HTTPException(status_code=400, detail="Адміністратор уже існує")

    new_admin = adminCrud.create_admin(
        db,
        admin.username,
        admin.password,
        admin.first_name,
        admin.last_name,
        admin.telegram_id
    )
    token = adminAuth.create_access_token({"sub": new_admin.username, "admin_id": new_admin.id}, db=db)
    return {"access_token": token, "token_type": "bearer"}


@router.post(
    "user/auth/register",
    response_model=adminSchemas.Token,
    summary="Реєстрація користувача",
    description="Створює нового користувача.",
    responses={200: {"description": "Користувач успішно зареєстрований"}})
def register_user(user: userSchemas.UserCreate, db: Session = Depends(get_db),
                  current_admin=Depends(get_current_admin)):
    db_user = userCrud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Користувач уже існує")

    new_user = userCrud.create_user(
        db,
        user.username,
        user.password,
        user.first_name,
        user.last_name,
        user.telegram_id
    )
    token = userAuth.create_access_token({"sub": new_user.username, "user_id": new_user.id}, db=db)
    return {"access_token": token, "token_type": "bearer"}


# --- LOGIN ---
@router.post("/auth/login",
             response_model=adminSchemas.Token,
             summary="Авторизація адміністратора",
             description="Авторизує адміністратора.",
             responses={200: {"description": "Адміністратор успішно авторизований"}}
             )
def login(
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)

):
    db_user = adminCrud.authenticate_admin(db, username, password)
    token = adminAuth.create_access_token({"sub": db_user.username, "admin_id": db_user.id}, db=db)
    return {"access_token": token, "token_type": "bearer"}


# --- LOGOUT ---
@router.post("/auth/logout",
             response_model=dict,
             summary="Вихід адміністратора з системи",
             description="Виконує вихід адміністратор і деактивує JWT токін в БД.",
             )
def logout(
        db: Session = Depends(get_db),
        current_admin=Depends(get_current_admin),
        token=Depends(oauth2_scheme)
):
    data = adminCrud.deactivate_token(db=db, token=token)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен вже недійсний або не знайдений"
        )
    return {"message": "Вихід успішний"}


@router.post("/",
             response_model=ReturnUsersGroup,
             summary="Створення групи (тільки для супер-адміна)",
             description="Створює групу (тільки для супер-адміна).",
             responses={200: {"description": "Група успішно створена"}}
             )
def create_group(group: CreateUsersGroup, db: Session = Depends(get_db),
                 current_admin=Depends(get_current_superadmin)):
    db_data = userCrud.get_group_by_name(db, group.name)
    print(db_data)
    if db_data:
        raise HTTPException(status_code=400, detail="Група уже існує")
    new_group = userCrud.create_group(
        db,
        group.name,
        group.description
    )
    return new_group


# --- LIST ---
@router.get("/admins-list",
            response_model=List[adminSchemas.User],
            summary="Отримати список адміністраторів в системі (тільки для супер-адміна) ",
            description="Отримує список адміністраторів в системі (тільки для супер-адміна)",
            responses={200: {"description": "Список отримано"}}
            )
def list_admin(db: Session = Depends(get_db), current_admin=Depends(get_current_superadmin)):
    return adminCrud.get_admins(db)


# --- GET BY ID ---
@router.get("/{admin_id}",
            response_model=adminSchemas.Admin,
            summary="Отримати адміністратора по ID (тільки для супер-адміна)",
            description="Отримує адміністратора по ID (тільки для супер-адміна)",
            responses={200: {"description": "Успішно отримано"}}
            )
def admin_by_id(admin_id: int, db: Session = Depends(get_db), current_admin=Depends(get_current_superadmin)):
    admin = adminCrud.get_admin_for_id(db=db, admin_id=admin_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Адміністратора з ID {admin_id} не знайдено"
        )
    return admin


@router.get("/users/users-list",
            response_model=List[userSchemas.User],
            summary="Отримати список користувачів в системі (тільки для супер-адміна) ",
            description="Отримує список користувачів в системі (тільки для супер-адміна)",
            responses={200: {"description": "Список отримано"}}
            )
def list_users(db: Session = Depends(get_db), current_admin=Depends(get_current_superadmin)):
    return userCrud.get_users(db)


@router.get("/users/group/group-list",
            response_model=List[userSchemas.ReturnUsersGroup],
            summary="Отримати список груп в системі (тільки для супер-адміна) ",
            description="Отримує список груп в системі (тільки для супер-адміна)",
            responses={200: {"description": "Список отримано"}}
            )
def list_group(db: Session = Depends(get_db), current_admin=Depends(get_current_superadmin)):
    return userCrud.get_groups(db)


@router.get("/users/group/{group_name}",
            response_model=userSchemas.ReturnUsersGroup,
            summary="Отримати групу по ID (тільки для супер-адміна)",
            description="Отримує групу по ID (тільки для супер-адміна)",
            responses={200: {"description": "Успішно отримано"}}
            )
def group_by_name(group_name: str, db: Session = Depends(get_db), current_admin=Depends(get_current_superadmin)):
    user = userCrud.get_group_by_name(db=db, group_name=group_name)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Групу за назвою {group_name} не знайдено"
        )
    return user


# --- UPDATE ---
@router.put(
    "/{admin_id}",
    response_model=adminSchemas.Admin,
    summary="Оновити адміністратора по ID (тільки для супер-адміна)",
    description="Оновлює дані адміністратора по його ID. Доступно лише супер-адміну.",
    responses={
        200: {"description": "Адміністратора успішно оновлено"},
        404: {"description": "Адміністратор не знайдений"},
        403: {"description": "Немає прав для оновлення"}
    }
)
def update_admin(
        admin_id: int,
        user_update: adminSchemas.AdminUpdate,
        db: Session = Depends(get_db),
        current_admin=Depends(get_current_superadmin)
):
    admin = adminCrud.get_admin_by_id(db, admin_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Адміністратора з ID {admin_id} не знайдено"
        )

    updated_admin = adminCrud.update_admin(db, admin, user_update)
    return updated_admin


@router.put(
    "/users/{user_id}",
    response_model=userSchemas.User,
    summary="Оновити користувача по ID (тільки для супер-адміна)",
    description="Оновлює дані користувача по його ID. Доступно лише супер-адміну.",
    responses={
        200: {"description": "користувача успішно оновлено"},
        404: {"description": "користувача не знайдений"},
        403: {"description": "Немає прав для оновлення"}
    }
)
def update_user(
        user_id: int,
        user_update: userSchemas.UserUpdate,
        db: Session = Depends(get_db),
        current_admin=Depends(get_current_superadmin)
):
    user = userCrud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Користувача з ID {user_id} не знайдено"
        )

    updated_user = userCrud.update_user(db, user, user_update)
    return updated_user


# --- DELETE ---
@router.delete("/{admin_id}",
               summary="Видалити адміністратора по ID (тільки для супер-адміна)",
               description="Видаляє адміністратора по ID (тільки для супер-адміна)",
               responses={200: {"description": "Успішно видаленно"}}
               )
def delete_admin(
        admin_id: int,
        db: Session = Depends(get_db),
        current_admin=Depends(get_current_superadmin)
):
    admin = adminCrud.get_admin_by_id(db, admin_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Адміністратора з ID {admin_id} не знайдено"
        )
    data = adminCrud.delete_admin(db, admin_id)
    return {"message": f"Адміністратор {admin.username} (ID={admin.id}) успішно видалений"}


@router.get("/{admin_id}/list-user-in-group",
            response_model=List[UserRead],
            summary="Знайти користувачів до яких адміністратор має доступ",
            description="Знаходе користувачів до яких адміністратор має доступ",
            responses={200: {"description": "Успішно отриманно"}}
            )
def get_users_for_admin(
        db: Session = Depends(get_db),
        current_admin=Depends(get_current_admin)
):
    admin_id = current_admin['payload']['admin_id']
    data = adminCrud.get_users_for_admin(db=db, admin_id=admin_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Користувач {admin_id} не має груп"
        )
    return data
