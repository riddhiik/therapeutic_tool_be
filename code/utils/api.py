import random
import re
from fastapi import HTTPException
from passlib.context import CryptContext

from models import Question
from schemas import QuestionSchema

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def validate_password(payload):
    if len(payload.password) < 8:
        raise HTTPException(
            status_code=400, detail="Password must be at least 8 characters long"
        )

    if not re.search(r"[a-z]", payload.password):
        raise HTTPException(
            status_code=400, detail="Password must include lowercase letters"
        )

    if not re.search(r"[A-Z]", payload.password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one uppercase letter",
        )

    if not re.search(r"\d", payload.password):
        raise HTTPException(
            status_code=400, detail="Password must contain at least one numeric digit"
        )

    if not re.search(r"[@#$!%*?&]", payload.password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one special character (e.g., !, @, #, $, %)",
        )


def get_random_questions(db, category=None, limit=10):
    if category:
        questions = db.query(Question).filter(Question.category == category).all()
    else:
        questions = db.query(Question).all()

    random.shuffle(questions)
    questions = questions[:limit]

    return [
        QuestionSchema(
            id=q.question_id, 
            question=q.question, 
            options=[q.option_1, q.option_2, q.option_3, q.option_4]
        ) 
        for q in questions
    ]
