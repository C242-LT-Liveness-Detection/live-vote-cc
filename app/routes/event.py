from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import schemas, event
from app.routes.auth import get_current_user

router = APIRouter(prefix="/events", tags=["Events"])

@router.post("/create")
def create_event(
    event_data: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    new_event = event.create_event(db, event_data, current_user.id)
    return {"message": "Event created successfully", "event": new_event.title, "unique_code": new_event.unique_code}