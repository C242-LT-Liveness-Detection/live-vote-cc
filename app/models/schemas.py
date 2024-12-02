from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from sqlmodel import Field
from datetime import datetime
from dateutil.parser import isoparse

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
    title: str = Field(..., min_length=1, max_length=255)
    question: str
    options: List[str]
    allow_multiple_votes: bool
    end_date: datetime
    
    @validator("end_date", pre=True)
    def validate_end_date(cls, value):
        try:
            parsed_date = isoparse(value)
        except ValueError:
            try:
                parsed_date = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                raise ValueError(
                    "Invalid datetime format."
                )
        
        if parsed_date <= datetime.now(parsed_date.tzinfo):
            raise ValueError("End date must be in the future.")
        
        return parsed_date

    @validator("options")
    def validate_options(cls, value):
        if len(value) < 2:
            raise ValueError("At least two options are required.")
        return value

    class Config:
        orm_mode = True

class JoinEventRequest(BaseModel):
    unique_code: str

    class Config:
        orm_mode = True

class OptionResponse(BaseModel):
    event_option_number: int
    option_text: str

    class Config:
        orm_mode = True

class EventResponse(BaseModel):
    unique_code: str
    title: str
    question: str
    created_date: datetime
    end_date: datetime
    options: List[OptionResponse]

    class Config:
        orm_mode = True

class CastVoteRequest(BaseModel):
    unique_code: str
    event_option_numbers: List[int]
    
    @validator("event_option_numbers")
    def validate_option_ids(cls, value):
        if len(value) != len(set(value)):
            raise ValueError("Duplicate option are not allowed.")
        if not value:
            raise ValueError("At least one option is required.")
        return value
    
class UserVoteResponse(BaseModel):
    event_title: str
    event_question: str
    event_unique_code: str
    vote_choices: List[OptionResponse]
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
