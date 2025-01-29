from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.orm import Session
from models import LoginLogs, Question, User, Therapy
from utils.api import get_random_questions
from schemas import AssessmentSubmit, QuestionCreate, QuestionSchema, UserCreate, login, TherapyCreate
from passlib.context import CryptContext
from db import SessionLocal, get_db

route = APIRouter(prefix="/assessment", tags=["Take Test"])


@route.get("/start", response_model=list[QuestionSchema])
def start_assessment(category: str = Query(None), limit: int = Query(10)):
    """
    Start an assessment by getting random questions. Optionally, filter by category.
    """
    db = SessionLocal()
    questions = get_random_questions(db, category, limit)
    db.close()
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found")
    return questions

@route.post("/submit")
def submit_assessment(data: AssessmentSubmit):
    """
    Submit answers to the assessment, calculate score, and update assessment and reassessment dates.
    """
    db = SessionLocal()
    
    try:
        # Fetch the user
        user = db.query(User).filter(User.id == data.userId).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        total_score = 0

        # Loop through the submitted answers and calculate the score
        for answer in data.answers:
            question = db.query(Question).filter(Question.id == answer.questionId).first()
            if not question:
                raise HTTPException(status_code=404, detail=f"Question with ID {answer.questionId} not found")

            # Score calculation based on the selected option
            if answer.selectedOption == question.option4:
                total_score += 3  # Assuming "Often" = 3
            elif answer.selectedOption == question.option3:
                total_score += 2
            elif answer.selectedOption == question.option2:
                total_score += 1


        user.assessment_score = total_score
        user.assessment_date = datetime.now().date()

        if total_score < 10:
            user.reassessment_date = datetime.now().date() + timedelta(days=30)
        elif 10 <= total_score <= 15:
            user.reassessment_date = datetime.now().date() + timedelta(days=15)
        else:
            user.reassessment_date = None 

        db.commit()

        return {"score": total_score, "message": "Score and dates have been successfully stored."}

    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred during assessment submission.")
    
    finally:
        db.close()



DEFAULT_OPTIONS = {
    "option_1": "Never",
    "option_2": "Sometimes",
    "option_3": "Often",
    "option_4": "Very Often",
}

# API to create a question with default options
@route.post("/create")
def create_question(payload: QuestionCreate):
    db: Session = SessionLocal()
    
    # Create a new question record with default options
    new_question = Question(
        category=payload.category,
        question=payload.question,
        option_1=payload.option_1,  
        option_2=payload.option_2,  
        option_3=payload.option_3, 
        option_4=payload.option_4 
    )
    
    # Add the new question to the database and commit
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    
    db.close()

    return {
        "message": "Question created successfully.",
        "question_id": new_question.question_id
        }