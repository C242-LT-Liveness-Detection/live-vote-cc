from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    unique_code = Column(String(20), unique=True, index=True)
    title = Column(String(255), nullable=False)
    choices = Column(Text, nullable=False)  # Stored as comma-separated values
    votes = relationship("Vote", back_populates="event")

class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"))
    voter_name = Column(String(100), nullable=False)
    voter_email = Column(String(100), nullable=False)
    choice = Column(String(255), nullable=False)
    liveness_photo = Column(Text, nullable=True)
    event = relationship("Event", back_populates="votes")