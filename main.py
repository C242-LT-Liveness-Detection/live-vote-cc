from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# In-memory database simulation
votes_db = {}
events_db = {}


# Models for input validation
class CreateEvent(BaseModel):
    question: str
    choices: list[str]


class CastVote(BaseModel):
    voter_name: str
    voter_email: str
    vote_choice: str
    liveness_photo: str  # Base64 string for the photo


# Routes
@app.get("/")
def home():
    return {"message": "Welcome to the Voting API!"}


@app.post("/create-event")
def create_event(event: CreateEvent):
    import uuid

    event_id = str(uuid.uuid4())[:8]  # Generate a short unique event ID
    events_db[event_id] = {
        "question": event.question,
        "choices": event.choices,
        "votes": {},
    }
    return {"message": "Event created successfully", "event_id": event_id}


@app.post("/cast-vote/{event_id}")
def cast_vote(event_id: str, vote: CastVote):
    if event_id not in events_db:
        raise HTTPException(status_code=404, detail="Event not found")
    event = events_db[event_id]

    if vote.vote_choice not in event["choices"]:
        raise HTTPException(
            status_code=400, detail="Invalid vote choice"
        )

    # Simulate saving voter details and vote
    voter_id = len(event["votes"]) + 1
    event["votes"][voter_id] = {
        "name": vote.voter_name,
        "email": vote.voter_email,
        "choice": vote.vote_choice,
        "liveness_photo": vote.liveness_photo,
    }

    return {"message": "Vote cast successfully", "voter_id": voter_id}


@app.get("/event-results/{event_id}")
def get_results(event_id: str):
    if event_id not in events_db:
        raise HTTPException(status_code=404, detail="Event not found")
    event = events_db[event_id]

    results = {choice: 0 for choice in event["choices"]}
    for vote in event["votes"].values():
        results[vote["choice"]] += 1

    return {"event": event["question"], "results": results}
