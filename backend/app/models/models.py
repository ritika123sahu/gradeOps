from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Enum, Float, Text
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum

class UserRole(str, enum.Enum):
    INSTRUCTOR = "instructor"
    TA = "ta"

class AnswerStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    OVERRIDDEN = "overridden"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default=UserRole.TA)

class Exam(Base):
    __tablename__ = "exams"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    rubric_json = Column(JSON) # List of questions with criteria
    instructor_id = Column(Integer, ForeignKey("users.id"))
    
    instructor = relationship("User")
    answers = relationship("StudentAnswer", back_populates="exam")

class StudentAnswer(Base):
    __tablename__ = "student_answers"
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"))
    student_id = Column(String, index=True)
    question_id = Column(String, index=True)
    
    image_path = Column(String)
    transcribed_text = Column(Text)
    
    ai_grade = Column(Float)
    ai_justification = Column(Text)
    
    ta_grade = Column(Float)
    status = Column(String, default=AnswerStatus.PENDING)
    
    exam = relationship("Exam", back_populates="answers")
