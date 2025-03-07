from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import random
import string
import bcrypt
import sqlite3
import jwt
import datetime
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()

# Подключение к БД
conn = sqlite3.connect("passwords.db", check_same_thread=False)
cursor = conn.cursor()

# Создание таблиц
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

# Функция генерации пароля
def generate_password(length: int, use_digits: bool, use_special: bool) -> str:
    chars = string.ascii_letters
    if use_digits:
        chars += string.digits
    if use_special:
        chars += string.punctuation
    return "".join(random.choice(chars) for _ in range(length))

# Функция хеширования пароля
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

# Функция поиска пользователя
def get_user(username: str):
    cursor.execute("SELECT id, username, hashed_password FROM users WHERE username = ?", (username,))
    return cursor.fetchone()  # Вернет (id, username, hashed_password) или None

# Функция проверки пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

# Регистрация пользователя
@app.post("/register/")
def register(user: RegisterRequest):
    hashed_password = hash_password(user.password)
    try:
        cursor.execute("INSERT INTO users (username, hashed_password) VALUES (?, ?)", (user.username, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "User registered successfully"}

# Функция создания JWT-токена
def create_jwt_token(username: str):
    payload = {
        "sub": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Авторизация пользователя (логин)
@app.post("/token/")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    
    if not user or not verify_password(form_data.password, user[2]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Генерируем токен
    access_token = create_jwt_token(user[1])
    return {"access_token": access_token, "token_type": "bearer"}

# Проверка токена
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Генерация пароля и сохранение в БД
@app.post("/generate/")
def generate(password_request: PasswordRequests, username: str = Depends(verify_token)):
    password = generate_password(password_request.length, password_request.use_digits, password_request.use_special)
    hashed_password = hash_password(password)

    # Получаем ID пользователя
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cursor.execute("INSERT INTO passwords (user_id, password) VALUES (?, ?)", (user[0], hashed_password))
    conn.commit()
    return {"password": password, "hashed_password": hashed_password}

# Проверка пароля пользователя
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

# Получение истории паролей (только своих)
@app.get("/history/")
def get_history(username: str = Depends(verify_token)):
    cursor.execute("SELECT password FROM passwords WHERE user_id = (SELECT id FROM users WHERE username = ?) ORDER BY id DESC LIMIT 10", (username,))
    return {"history": [row[0] for row in cursor.fetchall()]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
