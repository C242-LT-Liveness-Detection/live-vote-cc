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

    new_vote = Vote(
        event_id=event.id,
        voter_id=current_user.id
    )
    db.add(new_vote)
    db.commit()

    return {"message": f'Event "{event.title}" found. Please proceed with liveness detection before voting.'}

@router.get("/retrieve", response_model=List[schemas.EventResponse])
def get_all_events(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    events = db.query(Event).filter(Event.creator_id == current_user.id).order_by(Event.created_date.desc()).all()
    if not events:
        raise HTTPException(status_code=404, detail="No events found")
    return events

@router.post("/cast-vote")
def cast_vote(
    vote_data: schemas.CastVoteRequest,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    event = db.query(Event).filter(Event.unique_code == vote_data.unique_code).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    vote = db.query(Vote).filter(
        Vote.event_id == event.id,
        Vote.voter_id == current_user.id
    ).first()

    if not vote:
        raise HTTPException(status_code=400, detail="User has not joined this event")

    if any([getattr(vote, f"choice_{i}") for i in range(4)]):
        raise HTTPException(status_code=400, detail="You have already voted.")

    if event.allow_multiple_votes:
        for choice in vote_data.choices:
            if choice not in range(4):
                raise HTTPException(status_code=400, detail="Invalid choice")
            
            setattr(vote, f"choice_{choice}", True)
        db.commit()
        return {"message": f"Your votes have been cast for event '{event.title}'."}

    else:
        if vote_data.choices[0] not in range(4):
            raise HTTPException(status_code=400, detail="Invalid choice")
        
        setattr(vote, f"choice_{vote_data.choices[0]}", True)
        db.commit()
        return {"message": f"Your vote has been cast for event '{event.title}'."}
