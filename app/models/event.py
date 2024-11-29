from sqlalchemy.orm import Session
from app.db.database import Event, Option
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
        allow_multiple_votes=event_data.allow_multiple_votes,
        end_date=event_data.end_date,
        unique_code=unique_code
    )
    
    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    for option_text in event_data.options:
        add_option_to_event(db, event_id=new_event.id, option_text=option_text)

    return new_event

def add_option_to_event(db: Session, event_id: int, option_text: str):
    """Tambahkan opsi ke event tertentu dengan nomor urut per event."""
    max_number = db.query(Option).filter(Option.event_id == event_id).count()

    new_option = Option(
        event_id=event_id,
        option_text=option_text,
        event_option_number=max_number + 1
    )
    db.add(new_option)
    db.commit()
    db.refresh(new_option)

    return new_option