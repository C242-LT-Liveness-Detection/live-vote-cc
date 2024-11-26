from pydantic import BaseModel, EmailStr
from typing import Optional, List
from sqlmodel import Field
from datetime import datetime

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
    allow_multiple_votes: bool
    end_date: datetime

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

class EventResponse(BaseModel):
    unique_code: str
    title: str
    question: str
    created_date: datetime
    end_date: datetime

    class Config:
        orm_mode = True

class CastVoteRequest(BaseModel):
    unique_code: str
    choices: List[int]
    
class UserVoteResponse(BaseModel):
    event_title: str
    event_question: str
    event_unique_code: str
    vote_choices: List[str]
    voted_at: datetime

    class Config:
        orm_mode = True
        
class EventResultRequest(BaseModel):
    unique_code: str

    class Config:
        orm_mode = True

class VoteResult(BaseModel):
    option: str
    votes: int

        
class EventResultResponse(BaseModel):
    event_title: str
    event_question: str
    total_votes: int
    results: List[VoteResult]
    most_voted_option: Optional[str]

    class Config:
        orm_mode = True
