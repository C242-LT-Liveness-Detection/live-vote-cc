from fastapi import FastAPI
from app.routes import auth

app = FastAPI()

# Include authentication routes
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to LiveVote API"}
