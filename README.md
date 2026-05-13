# GradeOps: AI-Powered HITL Exam Grading

A complete pipeline for bulk exam grading using Qwen-VL for OCR and LangGraph for agentic grading.

## 🚀 Setup for macOS (Apple Silicon M1/M2/M3)

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- Docker Desktop
- Conda (recommended) or venv

### 2. Backend & ML Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate

# Install PyTorch with MPS support
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cpu

# Install dependencies
pip install fastapi uvicorn sqlalchemy asyncpg pydantic-settings python-multipart \
            python-jose[cryptography] passlib[bcrypt] transformers accelerate \
            langgraph langchain-openai pillow pymupdf
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 4. Infrastructure (Postgres & MinIO)
```bash
docker-compose up -d
```

## 🛠 Features
- **OCR/Vision**: Uses `Qwen-VL-Chat` optimized for `mps` device.
- **Agentic Pipeline**: LangGraph workflow (OCR -> Grading -> Plagiarism Check).
- **TA Dashboard**: High-speed review with keyboard shortcuts:
  - `A`: Approve AI Grade
  - `O`: Manual Override
  - `N`: Next Student
- **RBAC**: Instructor (Upload/Config) vs TA (Review) roles.

## 🍎 Apple Silicon (MPS) Notes
- The VLM loader in `ml/models/vlm.py` automatically detects and uses the `mps` device.
- PyTorch tensors are moved to `mps` for hardware-accelerated inference.
- Ensure `DEVICE=mps` is set in your `.env`.

## 📂 Project Structure
- `/backend`: FastAPI app & SQLAlchemy models.
- `/ml`: LangGraph agent, Qwen-VL loader, and PDF processor.
- `/frontend`: React (TypeScript) dashboard.
- `/data`: Local storage for PDF uploads and answer crops.
