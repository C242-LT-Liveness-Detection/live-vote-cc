from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.schemas import UserRegister, UserLogin
from app.models.user import User
from app.db.database import get_db
import hashlib

router = APIRouter()

@router.post("/register")
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    # Check if email is already registered
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")

    # Hash password
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()

    # Create new user
    new_user = User(name=user.name, email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "email": new_user.email}


@router.get("/login")
def login_user(email: str, password: str, db: Session = Depends(get_db)):
    # Find user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if user.password != hashed_password:
        raise HTTPException(status_code=401, detail="Incorrect password")

    return {"message": "Login successful", "user": {"name": user.name, "email": user.email}}
