from sqlalchemy.orm import Session
from app.db.database import Event, User
from app.models.schemas import EventCreate
import random
import string

def generate_unique_code(length: int = 5) -> str:
    """Generate a unique code for event."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

def create_event(db: Session, event_data: EventCreate, user_id: int):
    """Create a new event and save it to the database."""
    unique_code = generate_unique_code()

    new_event = Event(
        creator_id=user_id,
        title=event_data.title,
        question=event_data.question,
        choice_1=event_data.choice_1,
        choice_2=event_data.choice_2,
        choice_3=event_data.choice_3,
        choice_4=event_data.choice_4,
        unique_code=unique_code
    )
    
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event
