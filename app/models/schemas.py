from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlmodel import Field

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
    id: int = Field(default=None, primary_key=True)
    email: EmailStr
    name: str

    class Config:
        orm_mode = True

class EventCreate(BaseModel):
    title: str
    question: str
    choice_1: str
    choice_2: str
    choice_3: Optional[str] = None
    choice_4: Optional[str] = None

    class Config:
        orm_mode = True

class JoinEventRequest(BaseModel):
    unique_code: str

    class Config:
        orm_mode = True

class JoinEventResponse(BaseModel):
    message: str
    event_title: str

    class Config:
        orm_mode = True
