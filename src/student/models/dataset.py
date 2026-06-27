from typing import List

from pydantic import BaseModel, Field


class MinimalSource(BaseModel):
    file_path: str
    first_character_index: int
    last_character_index: int


class UnansweredQuestion(BaseModel):
    question_id: str
    question: str


class RagDataset(BaseModel):
    rag_questions: list[UnansweredQuestion]


class MinimalSearchResults(BaseModel):
    question_id: str
    question: str 
    retrieved_sources: list[MinimalSource]


class StudentSearchResults(BaseModel):
    search_results: list[MinimalSearchResults]
    k: int

class MinimalAnswer(MinimalSearchResults):
    answer: str

class StudentSearchResultsAndAnswer(StudentSearchResults):
    search_results: List[MinimalAnswer]