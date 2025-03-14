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
                   hashed_password TEXT
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


# Модели данных
class RegisterRequest(BaseModel):
    username: str
    password: str

class PasswordRequests(BaseModel):
    length: int
    use_digits: bool = True
    use_special: bool = False

class PasswordCheckRequest(BaseModel):
    password: str


history = []


def generate_password(length: int, use_digits: bool, use_special: bool) -> str:
    chars = string.ascii_letters
    if use_digits:
        chars += string.digits
    if use_special:
        chars += string.punctuation
    return "".join(random.choice(chars) for _ in range(length))


def get_user(username: str):
    cursor.execute("SELECT id, username, hashed_password FROM users WHERE username = ?", (username,))
    return cursor.fetchone()


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


@app.post("/register/")
def register(user: RegisterRequest):
    hashed_password = hash_password(user.password)
    try:
        cursor.execute("INSERT INTO users (username, hashed_password) VALUES(?,?)", (user.username, hashed_password))
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
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user[2]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_jwt_token(user[1])
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/generate/")
def generate(password_request: PasswordRequests, user: str = Depends(verify_token)):
    password = generate_password(password_request.length, password_request.use_digits, password_request.use_special)
    hashed_password = hash_password(password)
    cursor.execute("INSERT INTO passwords (password) VALUES (?)", (hashed_password,))
    conn.commit()
    return {"password": password, "hashed_password": hashed_password}


@app.post("/checkout/")
def checkout(password_check: PasswordCheckRequest, username: str = Depends(verify_token)):
    cursor.execute("SELECT password FROM passwords WHERE user_id = (SELECT id FROM users WHERE username = ?) ORDER BY id DESC LIMIT 1", (username,))
    last_password = cursor.fetchone()

    if not last_password:
        raise HTTPException(status_code=404, detail="No passwords found for user")

    if verify_password(password_check.password, last_password[0]):
        return {"message": "Password is correct"}
    else:
        raise HTTPException(status_code=401, detail="Invalid password")
        

def get_user_by_id(user_id: int):
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

def update_password(user_id: int, new_password: str):
    hashed_password = hash_password(new_password)
    cursor.execute("UPDATE users SET hashed_password = ? WHERE id = ?", (hashed_password, user_id))
    conn.commit()

def delete_user(user_id: int):
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()


@app.post("/update-password/")
def update_user_password(user_id: int, new_password: str):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    update_password(user_id, new_password)
    return {"message": "Password updated successfully"}


@app.post("/update-password/")
def update_password_for_user(user_id: int, new_password: str, current_user: str = Depends(verify_token)):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user != user[1]:  # Проверяем, что пользователь обновляет только свой пароль
        raise HTTPException(status_code=403, detail="Not authorized to change this password")
    update_password(user_id, new_password)
    return {"message": "Password updated successfully"}


@app.get("/users/")
def get_users(username: Optional[str] = None):
    if username:
        cursor.execute("SELECT * FROM users WHERE username LIKE ?", ('%' + username + '%',))
    else:
        cursor.execute("SELECT * FROM users")
    return {"users": cursor.fetchall()}



@app.get("/history/")
def get_history(user: str = Depends(verify_token)):
    cursor.execute("SELECT password FROM passwords ORDER BY id DESC LIMIT 10")
    return {"history": [row[0] for row in cursor.fetchall()]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)