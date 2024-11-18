from fastapi import APIRouter, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from app.models import schemas, user
from app.db.database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
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
    return {"message": "Login successful", "user": db_user.email}