from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class User(BaseModel):
    id: int
    email: EmailStr
    name: str

    class Config:
        orm_mode = True
