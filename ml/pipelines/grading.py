from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
import json
import re



class GradingState(TypedDict):
    image_path: str
    rubric: dict
    transcription: Optional[str]
    grade: Optional[float]
    justification: Optional[str]
    plagiarism_flag: bool
    error: Optional[str]


class GradingPipeline:
    def __init__(self, vlm_model):
        self.vlm = vlm_model
        self.workflow = self._create_workflow()

    def ocr_node(self, state: GradingState):
        try:
            text = self.vlm.transcribe(state["image_path"])
            return {"transcription": text}
        except Exception as e:
            return {"error": f"OCR Failed: {str(e)}"}

    def grading_node(self, state: GradingState):
        if state.get("error"):
            return {}

        transcription = state.get("transcription")
        if not transcription or transcription.startswith("Error:"):
            return {"error": "Invalid or empty transcription, skipping grading"}

        rubric = state["rubric"]
        question = rubric.get("question", "N/A")
        sample_answer = rubric.get("sample_answer", "N/A")
        max_marks = rubric.get("max_marks", 10)

        grading_prompt = f"""
You are an expert exam evaluator. Compare the Student Answer to the Expected Answer and provide a fair grade.

QUESTION:
{question}

EXPECTED ANSWER:
{sample_answer}

STUDENT ANSWER:
{transcription}

TASK:
1. Grade the answer out of {max_marks}
2. Give short justification
3. Mention missing concepts if any

OUTPUT FORMAT:
Grade: <number>
Justification: <text>
Missing Concepts: <text>
"""
        try:
            result = self.vlm.chat(grading_prompt)
            print(
                f"\n--- GRADING OUTPUT ---\n{result}\n----------------------\n")

            grade_match = re.search(
                r"Grade:\s*(\d+\.?\d*)", result, re.IGNORECASE)
            justification_match = re.search(
                r"Justification:\s*(.*)", result, re.IGNORECASE)

            return {
                "grade": float(grade_match.group(1)) if grade_match else 0.0,
                "justification": justification_match.group(1).strip() if justification_match else result.strip()
            }

        except Exception as e:
            return {"error": f"Grading Failed: {str(e)}"}

    def plagiarism_node(self, state: GradingState):
        # Stub for plagiarism check (In production, compare embeddings against vector store)
        return {"plagiarism_flag": False}

    def _create_workflow(self):
        workflow = StateGraph(GradingState)

        workflow.add_node("ocr", self.ocr_node)
        workflow.add_node("grade", self.grading_node)
        workflow.add_node("plagiarism", self.plagiarism_node)

        workflow.set_entry_point("ocr")
        workflow.add_edge("ocr", "grade")
        workflow.add_edge("grade", "plagiarism")
        workflow.add_edge("plagiarism", END)

        return workflow.compile()

    async def run(self, image_path: str, rubric: dict):
        initial_state = {
            "image_path": image_path,
            "rubric": rubric,
            "transcription": None,
            "grade": None,
            "justification": None,
            "plagiarism_flag": False,
            "error": None
        }
        return await self.workflow.ainvoke(initial_state)
