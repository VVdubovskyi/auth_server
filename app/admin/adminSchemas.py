from pydantic import BaseModel
from typing import Optional, List

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship


# Схеми для груп користувачів (імпортуємо з users)
class UserGroup(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    
    class Config:
        orm_mode = True

# Схема для користувачів (для адмінів)
class ManagedUser(BaseModel):
    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    telegram_id: Optional[str] = None
    group_id: Optional[int] = None
    group: Optional[UserGroup] = None
    
    class Config:
        orm_mode = True


class AdminUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    telegram_id: Optional[str] = None
    is_superadmin: Optional[bool] = False
    group_id: Optional[int] = None

# Схеми для адмінів
class AdminCreate(BaseModel):
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    telegram_id: Optional[str] = None

class AdminLogin(BaseModel):
    username: str
    password: str

class Admin(BaseModel):
    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    telegram_id: Optional[str] = None
    is_superadmin: int = 0  # 0 = звичайний адмін, 1 = головний адмін
    managed_user_groups: List[UserGroup] = []

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ManagedGroupsAssignment(BaseModel):
    user_group_ids: List[int]  # Список ID груп користувачів

# Для зворотної сумісності
UserCreate = AdminCreate
UserLogin = AdminLogin
User = Admin
