from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db, Event, Vote, Option, VoteOptions
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
    return {
        "message": "Event created successfully",
        "event": new_event.title,
        "unique_code": new_event.unique_code
    }

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

    has_voted = db.query(VoteOptions).filter(VoteOptions.vote_id == vote.id).first()
    if has_voted:
        raise HTTPException(status_code=400, detail="You have already voted.")

    valid_options = db.query(Option).filter(Option.event_id == event.id).all()
    valid_option_ids = [option.id for option in valid_options]

    if not all(option_id in valid_option_ids for option_id in vote_data.option_ids):
        raise HTTPException(status_code=400, detail="Invalid choice(s).")

    if not event.allow_multiple_votes and len(vote_data.option_ids) > 1:
        raise HTTPException(
            status_code=400, 
            detail="Multiple votes are not allowed for this event."
        )

    for option_id in vote_data.option_ids:
        vote_option = VoteOptions(
            vote_id=vote.id,
            option_id=option_id
        )
        db.add(vote_option)

    db.commit()

    return {"message": f"Your votes have been cast for event '{event.title}'."}

@router.post("/result", response_model=schemas.EventResultResponse)
def get_event_result(
    result_request: schemas.EventResultRequest,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    event = db.query(Event).filter(Event.unique_code == result_request.unique_code).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to view this event's results")

    results = []
    total_votes = 0

    # Ambil opsi dan hitung suara
    for option in event.options:
        vote_count = db.query(VoteOptions).filter(VoteOptions.option_id == option.id).count()
        total_votes += vote_count
        results.append({"option": option.option_text, "votes": vote_count})

    # Temukan opsi dengan suara terbanyak
    most_voted_option = max(results, key=lambda x: x["votes"], default=None)["option"] if results else None

    return {
        "event_title": event.title,
        "event_question": event.question,
        "total_votes": total_votes,
        "results": results,
        "most_voted_option": most_voted_option
    }
