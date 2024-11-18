from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:@localhost/livevote"

DEFAULT_DATABASE_URL = "mysql+pymysql://root:@localhost/"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

default_engine = create_engine(DEFAULT_DATABASE_URL, pool_pre_ping=True)

def create_database_if_not_exists():
    """Cek apakah database ada, jika tidak buat database baru."""
    try:
        with default_engine.connect() as conn:
            conn.execute("CREATE DATABASE IF NOT EXISTS livevote")
    except Exception as e:
        print(f"Failed to create database: {e}")

def get_db():
    """Get the database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()