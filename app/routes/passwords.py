import random
import string
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from schemas import PasswordCreate
from ..models import Password
from ..security import hash_password


router = APIRouter()


def generate_password(length: int, use_digits: bool, use_special: bool) -> str:
    chars = string.ascii_letters
    if use_digits:
        chars += string.digits
    if use_special:
        chars += string.punctuation
    return "".join(random.choice(chars) for _ in range(length))


@router.post("/generate/")
def generate(password_request: PasswordCreate, db: Session = Depends(get_db)):
    password = generate_password(password_request.length, password_request.use_digits, password_request.use_special)
    hashed_password = hash_password(password)
    
    
    db_password = Password(password=hashed_password)
    db.add(db_password)
    db.commit()
    
    return{"password": password, "hashed_password": hashed_password}
