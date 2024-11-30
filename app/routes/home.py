from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.routes.auth import get_current_user
from app.db.database import get_db, Event, Vote, Option
from typing import List
from app.models import schemas

router = APIRouter(prefix="/home", tags=["Home"])

@router.get("/retrieve", response_model=List[schemas.UserVoteResponse])
def get_user_votes(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    votes = db.query(Vote).filter(Vote.voter_id == current_user.id).order_by(Vote.joined_at.desc()).all()

    if not votes:
        raise HTTPException(status_code=404, detail="No votes found for the current user")

    user_votes = []
    for vote in votes:
        event = db.query(Event).filter(Event.id == vote.event_id).first()
        if not event:
            continue

        vote_choices = []
        for vote_option in vote.vote_options:
            option = db.query(Option).filter(Option.id == vote_option.option_id).first()
            vote_choices.append({
                "id": option.id,
                "option_text": option.option_text,
                "event_option_number": option.event_option_number
            })

        user_votes.append({
            "event_title": event.title,
            "event_question": event.question,
            "event_unique_code": event.unique_code,
            "vote_choices": vote_choices,
            "voted_at": vote.joined_at
        })

    return user_votes
