from fastapi import APIRouter, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from app.models import schemas, user
from app.db.database import get_db
import re

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Validator for email format
def validate_email(email: str):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        raise HTTPException(status_code=400, detail="Invalid email format")

# Validator for password
def validate_password(password: str):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    if not any(char.isdigit() for char in password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number")

@router.post("/register")
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    # Validate email format
    validate_email(user_data.email)

    # Check if name is empty
    if not user_data.name or user_data.name.strip() == "":
        raise HTTPException(status_code=400, detail="Name cannot be empty")

    # Validate password
    validate_password(user_data.password)

    # Check if email already exists
    existing_user = user.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
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
    return {"message": "Login successful", "user": db_user.email}