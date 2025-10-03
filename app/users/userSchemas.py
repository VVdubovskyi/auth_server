from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class UserRead(BaseModel):
    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Схеми для користувачів
class UserCreate(BaseModel):
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    telegram_id: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class User(BaseModel):
    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    telegram_id: Optional[str] = None
    group_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    telegram_id: Optional[str] = None
    group_id: Optional[int] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class GroupUsersBase(BaseModel):
    name: str
    description: Optional[str] = None


class CreateUsersGroup(GroupUsersBase):
    pass


class ReturnUsersGroup(GroupUsersBase):
    id: int
    users: List[UserRead] = []
    model_config = ConfigDict(from_attributes=True)
