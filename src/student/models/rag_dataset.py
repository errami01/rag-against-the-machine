from pydantic import BaseModel
from typing import List
from src.student.models.question import AnsweredQuestion, UnansweredQuestion


class RagDataset(BaseModel):
    rag_questions: List[AnsweredQuestion | UnansweredQuestion]