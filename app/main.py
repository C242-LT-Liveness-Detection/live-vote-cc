from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from app.routes import auth

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Include authentication routes
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to LiveVote API"}
