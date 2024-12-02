from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from pytz import timezone

DATABASE_NAME = "livevote"
DATABASE_URL = f"mysql+pymysql://root:@localhost/{DATABASE_NAME}"

engine_without_db = create_engine("mysql+pymysql://root:@localhost")
connection = engine_without_db.connect()

connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}"))
connection.close()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    
    votes = relationship("Vote", back_populates="voter")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    unique_code = Column(String(20), nullable=False, unique=True)
    question = Column(String(255), nullable=False)
    allow_multiple_votes = Column(Boolean, default=False)
    created_date = Column(DateTime, default=lambda: datetime.now(timezone("Asia/Jakarta")), nullable=False)
    end_date = Column(DateTime, nullable=False)

    votes = relationship("Vote", back_populates="event", cascade="all, delete-orphan")
    options = relationship("Option", back_populates="event", cascade="all, delete-orphan")
    
class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    option_text = Column(String(255), nullable=False)
    event_option_number = Column(Integer, nullable=False)

    event = relationship("Event", back_populates="options")
    vote_options = relationship("VoteOptions", back_populates="option", cascade="all, delete-orphan")

class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    voter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone("Asia/Jakarta")), nullable=False)
    already_vote = Column(Boolean, default=False)

    event = relationship("Event", back_populates="votes")
    voter = relationship("User", back_populates="votes")
    vote_options = relationship("VoteOptions", back_populates="vote", cascade="all, delete-orphan")
    
class VoteOptions(Base):
    __tablename__ = "vote_options"

    id = Column(Integer, primary_key=True, index=True)
    vote_id = Column(Integer, ForeignKey("votes.id", ondelete="CASCADE"), nullable=False)
    option_id = Column(Integer, ForeignKey("options.id", ondelete="CASCADE"), nullable=False)

    vote = relationship("Vote", back_populates="vote_options")
    option = relationship("Option", back_populates="vote_options")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
