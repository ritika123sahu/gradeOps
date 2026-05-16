from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from enum import Enum

class UserRole(str, Enum):
    INSTRUCTOR = "instructor"
    TA = "ta"

class UserBase(BaseModel):
    email: EmailStr
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ExamCreate(BaseModel):
    title: str
    rubric_json: Any

class ExamResponse(ExamCreate):
    id: int
    instructor_id: int
    class Config:
        from_attributes = True

class StudentAnswerResponse(BaseModel):
    id: int
    exam_id: int
    student_id: str
    question_id: str
    image_path: str
    transcribed_text: Optional[str]
    ai_grade: Optional[float]
    ai_justification: Optional[str]
    ta_grade: Optional[float]
    status: str
    class Config:
        from_attributes = True
