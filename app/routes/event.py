from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db, Event, Vote, Option, VoteOptions
from app.models import schemas, event
from app.routes.auth import get_current_user
from app.models.schemas import EventResponse, OptionResponse
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
    
    if current_user.id == event.creator_id:
        raise HTTPException(status_code=400, detail="You cannot join an event you created.")
    
    if datetime.now() > event.end_date:
        raise HTTPException(status_code=400, detail="Event has already ended. You can no longer join.")

    existing_vote = db.query(Vote).filter(
        Vote.event_id == event.id,
        Vote.voter_id == current_user.id
    ).first()

    if existing_vote:
        if existing_vote.already_vote:
            raise HTTPException(status_code=400, detail="You have already voted, cannot join again.")
        else:
            return {"message": f'Event "{event.title}" found. Please proceed with liveness detection before voting.'}
    else:
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

@router.get("/{unique_code}", response_model=EventResponse)
def get_event_details(
    unique_code: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    event = db.query(Event).filter(Event.unique_code == unique_code).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    options = db.query(Option).filter(Option.event_id == event.id).all()
    if not options:
        raise HTTPException(status_code=404, detail="No options found for this event")

    event_data = EventResponse(
        unique_code=event.unique_code,
        title=event.title,
        question=event.question,
        created_date=event.created_date,
        end_date=event.end_date,
        options=[
            OptionResponse(
                event_option_number=opt.event_option_number, 
                option_text=opt.option_text
            ) 
            for opt in options
        ]
    )
    
    return event_data

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

    if vote.already_vote:
        raise HTTPException(status_code=400, detail="You have already voted.")

    has_voted = db.query(VoteOptions).filter(VoteOptions.vote_id == vote.id).first()
    if has_voted:
        raise HTTPException(status_code=400, detail="You have already voted.")

    valid_options = db.query(Option).filter(Option.event_id == event.id).all()
    valid_option_numbers = [option.event_option_number for option in valid_options]

    if not all(option_number in valid_option_numbers for option_number in vote_data.event_option_numbers):
        raise HTTPException(status_code=400, detail="Invalid choice(s).")

    if not event.allow_multiple_votes and len(vote_data.event_option_numbers) > 1:
        raise HTTPException(
            status_code=400, 
            detail="Multiple votes are not allowed for this event."
        )

    for option_number in vote_data.event_option_numbers:
        option = db.query(Option).filter(Option.event_option_number == option_number, Option.event_id == event.id).first()
        if option:
            vote_option = VoteOptions(
                vote_id=vote.id,
                option_id=option.id
            )
            db.add(vote_option)
        else:
            raise HTTPException(status_code=400, detail=f"Option with number {option_number} not found.")
    
    vote.already_vote = True
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

    for option in event.options:
        vote_count = db.query(VoteOptions).filter(VoteOptions.option_id == option.id).count()
        total_votes += vote_count
        results.append({"option": option.option_text, "votes": vote_count})

    most_voted_option = max(results, key=lambda x: x["votes"], default=None)["option"] if results else None

    return {
        "event_title": event.title,
        "event_question": event.question,
        "total_votes": total_votes,
        "results": results,
        "most_voted_option": most_voted_option
    }
