from fastapi import FastAPI
from .routes import auth, passwords
from .database import engine, Base


Base.metadata.create_all(bind=engine)


app = FastAPI()


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(passwords.router, prefix="passwords", tags=["passwords"])