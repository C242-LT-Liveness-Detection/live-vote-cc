from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db, Event, Vote
from app.models import schemas, event
from app.routes.auth import get_current_user
from datetime import datetime

router = APIRouter(prefix="/events", tags=["Events"])

@router.post("/create")
def create_event(
    event_data: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    new_event = event.create_event(db, event_data, current_user.id)
    return {"message": "Event created successfully", "event": new_event.title, "unique_code": new_event.unique_code}

@router.post("/join")
def join_event(
    join_data: schemas.JoinEventRequest,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    event = db.query(Event).filter(Event.unique_code == join_data.unique_code).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if datetime.now() > event.end_date:
        raise HTTPException(status_code=400, detail="Event has already ended. You can no longer join.")

    existing_vote = db.query(Vote).filter(
        Vote.event_id == event.id,
        Vote.voter_id == current_user.id
    ).first()
    if existing_vote:
        raise HTTPException(status_code=400, detail="User has already joined this event")

    new_vote = Vote(event_id=event.id, voter_id=current_user.id, choice="")
    db.add(new_vote)
    db.commit()

    return {"message": f'Event "{event.title}" found. Please proceed with liveness detection before voting.'}

@router.get("/retrive", response_model=List[schemas.EventResponse])
def get_all_events(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    events = db.query(Event).filter(Event.creator_id == current_user.id).order_by(Event.created_date.desc()).all()
    if not events:
        raise HTTPException(status_code=404, detail="No events found")
    return events