from sqlalchemy.orm import Session
from app.db.database import User
from app.models.schemas import UserCreate
from hashlib import sha256

def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()

def create_user(db: Session, user_data: UserCreate):
    hashed_password = hash_password(user_data.password)
    new_user = User(email=user_data.email, name=user_data.name, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    hashed_password = hash_password(password)
    return db.query(User).filter(User.email == email, User.password == hashed_password).first()
