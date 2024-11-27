from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from app.routes import auth, event, home

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

app.include_router(auth.router)
app.include_router(event.router)
app.include_router(home.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to LiveVote API"}
