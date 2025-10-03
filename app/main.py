from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from admin import adminModels, adminRoutes
from core.database import Base, engine
from users import userModels, userRoutes
from core import database
Base.metadata.create_all(bind=engine)


# Метадані для документації API
description = """
## 🔐 Сервіс Аутентифікації та Управління Користувачами

Цей API надає функціонал для управління користувачами, адміністраторами та їх групами.

### Основні можливості:

#### 👥 Користувачі (Users)
* Реєстрація та аутентифікація користувачів
* Управління профілями користувачів
* Створення та управління групами користувачів
* Призначення користувачів до груп

#### 👨‍💼 Адміністратори (Admins)
* Реєстрація та аутентифікація адміністраторів
* Управління профілями адміністраторів
* Створення та управління групами адміністраторів
* Призначення адміністраторів до груп адміністраторів
* Призначення груп користувачів для управління адміном
* Перегляд користувачів, доступних адміну через керовані групи

### Архітектура:
* **Адміністратори** можуть належати до **груп адміністраторів** (для організації)
* **Адміністраторам** можна призначити **групи користувачів** для управління
* **Користувачі** можуть належати до **груп користувачів**
* Адмін бачить тільки тих користувачів, які належать до груп, якими він управляє
"""

app = FastAPI(
    title="🔐 Auth Service API",
    description=description,
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@authservice.com",
    },
    license_info={
        "name": "MIT",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:5173"],  # або ["*"] для всіх
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    adminRoutes.router, 
    prefix="/api/admin", 
    tags=["👨‍💼 Адміністратори"],
    responses={404: {"description": "Не знайдено"}}
)
app.include_router(
    userRoutes.router, 
    prefix="/api/users", 
    tags=["👥 Користувачі"],
    responses={404: {"description": "Не знайдено"}}
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
