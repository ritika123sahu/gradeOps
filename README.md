# GradeOps: AI-Powered Exam Grading & Review Platform

GradeOps is a full-stack platform designed to automate the transcription and evaluation of handwritten exams. It utilizes local Vision-Language Models (VLM) and an agentic workflow to provide a Human-In-The-Loop (HITL) grading experience, ensuring high accuracy while maintaining strict data privacy.

## Project Overview

The system automates the transition from physical exam papers to graded digital records. It processes bulk PDF uploads, partitions them into individual student answers, and applies a multi-stage AI pipeline to transcribe handwriting and evaluate responses against a structured rubric.

### System Architecture

-   **Frontend**: A React.js (TypeScript) dashboard designed for high-throughput review. It features keyboard-driven navigation to allow TAs to rapidly approve or override AI-generated grades.
-   **Backend**: A FastAPI (Python) REST API that manages the orchestration of the ML pipeline, user authentication (RBAC), and asynchronous database persistence.
-   **ML Pipeline**: Built with **LangGraph**, the pipeline treats grading as a state-machine workflow (OCR Node -> Grading Node -> Plagiarism Check), allowing for modular reasoning and higher reliability than single-prompt approaches.
-   **Database**: PostgreSQL for structured storage of exams, rubrics, student answers, and audit trails.

## Technical Highlights

-   **Local VLM Inference**: Powered by **Qwen2-VL**, the system performs on-device OCR and semantic evaluation. It is optimized for Apple Silicon via **Metal Performance Shaders (MPS)**, utilizing `bfloat16` precision for efficient GPU-accelerated inference.
-   **HITL Workflow**: The system is built on the principle that AI assists rather than replaces the educator. Every AI-generated grade is queued for human verification in the TA Dashboard.
-   **Handwriting OCR**: Specifically tuned to handle the variability of handwritten text in academic settings, converting visual input into structured Markdown transcription.
-   **Privacy & Compliance**: By running models locally, GradeOps ensures that sensitive student data (PII) never leaves the local environment, satisfying strict institutional privacy requirements.

## Performance & Optimization

-   **Memory Management**: Implements dynamic image resizing and PIL decompression-bomb protection to handle high-resolution (300+ DPI) scans without system memory overflow.
-   **Greedy Decoding**: The OCR process is configured for greedy decoding with a repetition penalty to maximize the accuracy of verbatim transcriptions.
-   **Real-time Streaming**: Utilizes `TextStreamer` to provide real-time feedback in the server logs during the transcription and grading phases.

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker (for PostgreSQL)

### Installation
1.  **Backend**:
    ```bash
    cd backend
    python -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    ```
2.  **Frontend**:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```
3.  **Database**:
    ```bash
    docker-compose up -d
    ```

## Technology Stack
- **Language**: Python, TypeScript
- **AI Frameworks**: Transformers, LangGraph, PyTorch (MPS)
- **Web**: FastAPI, React, Vite
- **Storage**: PostgreSQL, SQLAlchemy (Async)

## Demo video


https://github.com/user-attachments/assets/423564c3-cc22-45e2-8c38-ef598debd9df

