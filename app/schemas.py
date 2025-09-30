from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True  # дозволяє SQLAlchemy-моделі конвертуватися у Pydantic

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
