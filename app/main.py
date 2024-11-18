from fastapi import FastAPI
from app.routes import auth
from app.db.database import Base, engine

# Initialize database
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include authentication routes
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

@app.get("/")
def home():
    return {"message": "Welcome to LiveVote API"}