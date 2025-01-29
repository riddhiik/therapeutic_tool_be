from random import random
import string
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    JSON,
    String,
    BigInteger,
    DATE,
    Float,
    Computed,
    DateTime,
    Enum,
    ARRAY,
    Text,
    event,
    TIMESTAMP,
)
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID
from db import Base

from config import setting

def generate_uuid():
    return str(uuid.uuid4().hex)


class User(Base):
    __tablename__ = "user"

    id = Column(Integer,nullable=False, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, default="")
    gender = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    dob = Column(DATE, nullable=True)
    parent_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    assessment_score = Column(Float, nullable=True)
    assessment_date = Column(Date, nullable=True)
    reassessment_date = Column(Date, nullable=True)
    reassessment_score = Column(Float, nullable=True)

class LoginLogs(Base):
    __tablename__ = "login_logs"
    id = Column(Integer, primary_key=True, index=True)
    ph = Column(Integer, nullable=True)
    email = Column(String, nullable=True)
    datetime = Column(DateTime, server_default=func.now(), nullable=False)

class Question(Base):
    __tablename__ = "assessment"
    
    question_id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # Set as primary key
    category = Column(String(255), index=True)
    question = Column(Text, nullable=False)
    option_1 = Column(String(255), nullable=False)
    option_2 = Column(String(255), nullable=False)
    option_3 = Column(String(255), nullable=False)
    option_4 = Column(String(255), nullable=False)


class Therapy(Base):
    __tablename__ = "therapy"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)  
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    therapy_duration = Column(Integer, nullable=False)