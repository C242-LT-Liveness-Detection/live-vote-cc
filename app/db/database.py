from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_NAME = "livevote"
DATABASE_URL = f"mysql+pymysql://root:@localhost/{DATABASE_NAME}"

# Connect to MySQL server
engine_without_db = create_engine("mysql+pymysql://root:@localhost")
connection = engine_without_db.connect()

# Execute raw SQL to create the database if it doesn't exist
connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}"))
connection.close()

# Connect to the database
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define tables
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    unique_code = Column(String(20), nullable=False)
    question = Column(String(255), nullable=False)
    choice_1 = Column(String(255), nullable=False)
    choice_2 = Column(String(255), nullable=False)
    choice_3 = Column(String(255), nullable=True)
    choice_4 = Column(String(255), nullable=True)

class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    voter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    choice = Column(String(255), nullable=False)

# Initialize the database and tables
Base.metadata.create_all(bind=engine)

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
