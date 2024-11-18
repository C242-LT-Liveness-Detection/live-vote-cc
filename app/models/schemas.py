from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

    class Config:
        orm_mode = True

class User(BaseModel):
    id: int
    email: EmailStr
    name: str

    class Config:
        orm_mode = True
