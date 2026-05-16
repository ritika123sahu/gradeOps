from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import os
import json
from contextlib import asynccontextmanager

from app.db.session import get_db, engine, Base, SessionLocal
from app.models.models import User, Exam, StudentAnswer, UserRole
from ml.utils.pdf_processor import split_pdf_to_images
from app.schemas.schemas import UserCreate, UserResponse, Token, ExamCreate, ExamResponse, StudentAnswerResponse
from app.core.security import verify_password, get_password_hash, create_access_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from app.core.security import SECRET_KEY, ALGORITHM
from fastapi.staticfiles import StaticFiles


# Runs during FastAPI startup to initialize database tables
# and create default Instructor and TA accounts if they don't already exist
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as db:
        for email, role in [("instructor@test.com", UserRole.INSTRUCTOR), ("ta@test.com", UserRole.TA)]:
            result = await db.execute(select(User).where(User.email == email))
            if not result.scalars().first():
                user = User(email=email, hashed_password=get_password_hash("password123"), role=role)
                db.add(user)
        await db.commit()
    yield

# Define absolute path for data directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

app = FastAPI(title="GradeOps API", lifespan=lifespan)
app.mount("/data", StaticFiles(directory=DATA_DIR), name="data")

@app.get("/")
async def root():
    return {"message": "GradeOps API is running"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if user is None: raise HTTPException(status_code=401)
        return user
    except: raise HTTPException(status_code=401)

@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    return {"access_token": create_access_token(subject=user.email), "token_type": "bearer"}

@app.post("/exams/upload", response_model=ExamResponse)
async def upload_exam(
    title: str, 
    rubric: str, 
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.INSTRUCTOR:
        raise HTTPException(status_code=403)
    
    upload_dir = os.path.join(DATA_DIR, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    # Split PDF into images (One image = One Student)
    crops_dir = os.path.join(DATA_DIR, "crops")
    image_paths = split_pdf_to_images(file_path, crops_dir)
    
    cleaned_rubric = rubric.replace('\n', ' ').replace('\r', '').replace('\t', ' ')
    rubric_obj = json.loads(cleaned_rubric)
    
    exam = Exam(title=title, rubric_json=rubric_obj, instructor_id=current_user.id)
    db.add(exam)
    await db.commit()
    await db.refresh(exam)

    from ml.models.vlm import QwenVLModel
    from ml.pipelines.grading import GradingPipeline

    qwen_model = QwenVLModel()
    grading_pipeline = GradingPipeline(qwen_model)
    
    # Process each student page
    for i, img_path in enumerate(image_paths):
        result = await grading_pipeline.run(img_path, rubric_obj)

        grade_text = result.get("grade")
        justification = result.get("justification")
        transcription = result.get("transcription")
        error = result.get("error")

        ans = StudentAnswer(
            exam_id=exam.id,
            student_id=f"STUDENT_{i+1:03d}",
            question_id="Q1",
            image_path=img_path,
            transcribed_text=transcription if transcription else "",
            ai_grade=float(grade_text) if grade_text is not None else 0.0,
            ai_justification=justification if justification else (f"Grading error: {error}" if error else "No justification provided."),
            status="pending"
        )
        db.add(ans)
    
    await db.commit()
    await db.refresh(exam)
    return exam

@app.get("/answers/pending", response_model=List[StudentAnswerResponse])
async def get_pending_answers(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StudentAnswer).where(StudentAnswer.status == "pending"))
    return result.scalars().all()

@app.post("/answers/{answer_id}/approve")
async def approve_answer(answer_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StudentAnswer).where(StudentAnswer.id == answer_id))
    answer = result.scalars().first()
    if not answer: raise HTTPException(status_code=404)
    answer.status = "approved"
    answer.ta_grade = answer.ai_grade
    await db.commit()
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
