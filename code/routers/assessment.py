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
def start_assessment(category: str = Query(None)):
    """
    Start an assessment by getting random questions. Optionally, filter by category.
    """
    db = SessionLocal()
    questions = get_random_questions(db, category)
    db.close()
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found")
    return questions


@route.post("/submit")
def submit_assessment(data: AssessmentSubmit):
    """
    Submit answers to the assessment, calculate score, and update assessment and reassessment dates.
    Also creates therapy entry based on percentage score thresholds.
    """
    db = SessionLocal()
    
    try:
        # Fetch the user
        user = db.query(User).filter(User.id == data.userId).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user is currently in therapy
        current_therapy = db.query(Therapy).filter(
            Therapy.user_id == user.id,
            Therapy.end_date >= datetime.now().date()
        ).first()
        
        if current_therapy:
            raise HTTPException(
                status_code=400, 
                detail="Assessment cannot be taken during active therapy period"
            )

        total_score = 0
        max_possible_score = 100  # 25 questions × 4 points
        
        # Loop through the submitted answers and calculate the score
        for answer in data.answers:
            question = db.query(Question).filter(Question.id == answer.questionId).first()
            if not question:
                raise HTTPException(status_code=404, detail=f"Question with ID {answer.questionId} not found")
            
            # Handle scoring based on different option formats
            selected = answer.selectedOption.lower() if isinstance(answer.selectedOption, str) else answer.selectedOption
            
            # Direct option reference (option1, option2, etc.)
            if selected == "option4" or selected == question.option4:
                total_score += 4
            elif selected == "option3" or selected == question.option3:
                total_score += 3
            elif selected == "option2" or selected == question.option2:
                total_score += 2
            elif selected == "option1" or selected == question.option1:
                total_score += 1
            # Handle by keywords in option text
            elif isinstance(selected, str):
                if "often" in selected.lower() or "frequently" in selected.lower():
                    total_score += 4
                elif "sometimes" in selected.lower():
                    total_score += 3
                elif "rarely" in selected.lower():
                    total_score += 2
                elif "never" in selected.lower():
                    total_score += 1
            # Handle numeric values
            elif isinstance(selected, int):
                total_score += min(max(selected, 1), 4)  # Ensure value is between 1-4

        user.assessment_score = total_score
        user.assessment_date = datetime.now().date()
        
        # Determine therapy duration based on score
        therapy_duration = None
        if total_score >= 80:
            therapy_duration = 3  # 3 months
        elif 60 <= total_score < 80:
            therapy_duration = 2  # 2 months
        elif 40 <= total_score < 60:
            therapy_duration = 1  # 1 month
        
        # Create therapy entry if needed
        if therapy_duration:
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=30 * therapy_duration)
            
            new_therapy = Therapy(
                user_id=user.id,
                start_date=start_date,
                end_date=end_date,
                therapy_duration=therapy_duration
            )
            db.add(new_therapy)
            
            # Set reassessment date after therapy ends
            user.reassessment_date = end_date + timedelta(days=1)
        else:
            # No therapy needed (score < 40)
            # Set reassessment date based on original logic
            if total_score < 10:
                user.reassessment_date = datetime.now().date() + timedelta(days=30)
            elif 10 <= total_score <= 15:
                user.reassessment_date = datetime.now().date() + timedelta(days=15)
            else:
                user.reassessment_date = datetime.now().date() + timedelta(days=7)

        db.commit()

        # Prepare response with detailed information
        result = {
            "score": total_score,
            "max_possible_score": max_possible_score,
            "percentage": round((total_score / max_possible_score) * 100, 2),
            "message": "Assessment submitted successfully."
        }
        
        if therapy_duration:
            result["therapy"] = {
                "duration": f"{therapy_duration} month(s)",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "reassessment_date": user.reassessment_date.isoformat()
            }
        else:
            result["message"] += " No therapy required based on your score."
            result["reassessment_date"] = user.reassessment_date.isoformat() if user.reassessment_date else None

        return result

    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        else:
            print(f"Error in submit_assessment: {str(e)}")
            raise HTTPException(status_code=500, detail=f"An error occurred during assessment submission: {str(e)}")
    
    finally:
        db.close()


DEFAULT_OPTIONS = {
    "option1": "Never",
    "option2": "Sometimes",
    "option3": "Often",
    "option4": "Very Often",
}

# API to create a question with default options
@route.post("/create")
def create_question(payload: QuestionCreate):
    db: Session = SessionLocal()
    
    # Create a new question record with default options
    new_question = Question(
        category=payload.category,
        question=payload.question,
        option1=payload.option1,  
        option2=payload.option2,  
        option3=payload.option3, 
        option4=payload.option4 
    )
    
    # Add the new question to the database and commit
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    
    db.close()

    return {
        "message": "Question created successfully.",
        "id": new_question.id
        }