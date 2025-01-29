from datetime import date, datetime
from re import compile
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, constr
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Optional, Literal
import re
from db import get_db


class GetUser(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    name: str


class UserCreate(BaseModel):
    name: str
    gender: Optional[str] = None
    age: Optional[int] = None
    dob: Optional[date] = None
    parent_name: Optional[str] = None
    email: EmailStr
    password: str
    phone_number: str


class UserUpdate(UserCreate):
    assessment_score: Optional[float]
    assessment_date: Optional[date]
    reassessment_date: Optional[date]
    reassessment_score: Optional[float]

class UserResponse(UserCreate):
    assessment_score: Optional[float] = None
    assessment_date: Optional[date] = None
    reassessment_date: Optional[date] = None
    reassessment_score: Optional[float] = None

    class Config:
        from_attributes = True


class login(BaseModel):
    email: EmailStr
    password: str

class QuestionSchema(BaseModel):
    id: int
    question: str
    options: list[str]

class AnswerSchema(BaseModel):
    questionId: int
    selectedOption: str

class AssessmentSubmit(BaseModel):
    userId: int
    answers: list[AnswerSchema]

class TherapyCreate(BaseModel):
    user_id: int
    start_date: date
    therapy_duration: int

class QuestionCreate(BaseModel):
    category: str  
    question: str
    option_1: str = "Never"
    option_2: str = "Sometimes"
    option_3: str = "Often"
    option_4: str = "Always"