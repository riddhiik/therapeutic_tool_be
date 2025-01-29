from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import Therapy, User
from schemas import TherapyCreate
from db import SessionLocal

route = APIRouter(prefix="/therapy", tags=["Therapy"])

@route.post("/create")
def create_therapy(payload: TherapyCreate):
    db: Session = SessionLocal()
    
    # Check if the user exists in the database
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate the end date
    end_date = payload.start_date + timedelta(days=payload.therapy_duration)
    
    # Create a new Therapy record
    new_therapy = Therapy(
        user_id=payload.user_id,
        start_date=payload.start_date,
        end_date=end_date,
        therapy_duration=payload.therapy_duration  # Store the duration in the new column
    )
    
    # Add the new therapy record to the session and commit
    db.add(new_therapy)
    db.commit()
    db.refresh(new_therapy)
    
    db.close()

    return {
        "message": "Therapy created successfully.",
        "therapy_id": new_therapy.id
    }
@route.get("/")
def get_therapy():
    return {"message": "Therapy route is working!"}
