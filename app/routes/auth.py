from fastapi import APIRouter, HTTPException, Depends, Form, status
from sqlalchemy.orm import Session
from app.models import schemas, user
from app.db.database import get_db
from app.utils.jwt_utils import create_access_token, verify_token
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta
import re

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> schemas.User:
    user_info = verify_token(token)
    if not user_info:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    email = user_info.get('sub')
    
    db_user = user.get_user_by_email(db, email)
    
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return db_user

def validate_email(email: str):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        raise HTTPException(status_code=400, detail="Invalid email format")

def validate_password(password: str):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    if not any(char.isdigit() for char in password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number")

@router.post("/register")
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    validate_email(user_data.email)

    if not user_data.name or user_data.name.strip() == "":
        raise HTTPException(status_code=400, detail="Name cannot be empty")

    validate_password(user_data.password)

    existing_user = user.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = user.create_user(db, user_data)
    return {"message": "User registered successfully", "user": new_user.email}

@router.post("/login")
def login(
    email: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    db_user = user.authenticate_user(db, email, password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": db_user.email})
    return {"message": "Login successful", "access_token": access_token, "token_type": "bearer"}
