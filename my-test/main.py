from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import random
import string
import bcrypt
import sqlite3
import jwt
import datetime
from typing import Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm



app = FastAPI()


conn = sqlite3.connect("passwords.db", check_same_thread=False0)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NO EXISTS passwords (id INTEGER PRIMARY KEY, password TEXT )")
conn.commit()


SECRET_KEY = "schailehmon141"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class PasswordRequests(BaseModel):
    length: int
    use_digits: bool = True
    use_special: bool = False


history = []


def generate_password(length: int, use_digits: bool, use_special: bool) -> str:
    chars = string.ascii_letters
    if use_digits:
        chars += string.digits
    if use_special:
        chars += string.punctuation
    return "".join(random.choice(chars) for _ in range(length))


@app.post("/generate/")
def generate(password_request: PasswordRequests):
    password = generate_password(password_request.length, password_request.use_digits, password_request.use_special)
    return {"password": password}


@app.get("/history/")
def get_history():
    return {"history": history[-10]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
    