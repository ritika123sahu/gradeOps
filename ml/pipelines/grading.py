from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
import json

# Define the state of our grading agent
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
        if state.get("error"): return state
        
        # Mocking LLM grading logic (In production, use LangChain with GPT-4o or Qwen-2)
        transcription = state["transcription"]
        rubric = state["rubric"]
        
        # Logic: Compare transcription to sample_answer in rubric
        # This is a stub for the prompt-based grading
        grade = rubric.get("max_marks", 10) * 0.8 # Mock 80% score
        justification = f"The student correctly identified the core concepts of {rubric.get('question', 'the question')} but missed minor details."
        
        return {"grade": grade, "justification": justification}

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
