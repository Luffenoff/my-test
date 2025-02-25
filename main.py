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


conn = sqlite3.connect("passwords.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS passwords (id INTEGER PRIMARY KEY, password TEXT )")
cursor.execute("""
               CREATE TABLE IF NOT EXISTS users (
                   id INTEGER PRIMARY KEY,
                   username TEXT UNIQUE,
                   hashes_password TEXT
               )
""")
cursor.execute("""
               CREATE TABLE IF NOT EXISTS passwords (
                   id INTEGER PRIMARY KEY,
                   user_id INTEGER,
                   password TEXT,
                   FOREIGN KEY(user_id) REFERENCES users(id)
               )
""")
conn.commit()


SECRET_KEY = "schailehmon141"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class RegisterRequest(BaseModel):
    username: str
    password: str

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


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


@app.post("/register/")
def register(user: RegisterRequest):
    hashed_password = hash_password(user.password)
    try:
        cursor.execute("INSER INTO users (username, hashed_password) VALUES(?,?)", (user.username, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "User registered successfully"}

def create_jwt_token(username: str):
    payload = {
            "sub": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/token/")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == "admin" and form_data.password == "password":
        return {"access_token": create_jwt_token(form_data.username), "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/generate/")
def generate(password_request: PasswordRequests, user: str = Depends(verify_token)):
    password = generate_password(password_request.length, password_request.use_digits, password_request.use_special)
    hashed_password = hash_password(password)
    cursor.execute("INSERT INTO passwords (password) VALUES (?)", (hashed_password,))
    conn.commit()
    return {"password": password, "hashed_password": hashed_password}


@app.get("/history/")
def get_history(user: str = Depends(verify_token)):
    cursor.execute("SELECT password FROM passwords ORDER BY id DESC LIMIT 10")
    return {"history": [row[0] for row in cursor.fetchall()]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
    