from typing import List

from pydantic import BaseModel, ConfigDict, Field


class MinimalSource(BaseModel):
    file_path: str
    first_character_index: int
    last_character_index: int


class UnansweredQuestion(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    question_id: str
    question: str = Field(..., alias="question_str")


class AnsweredQuestion(UnansweredQuestion):
    sources: List[MinimalSource]
    answer: str

class RagDataset(BaseModel):
    rag_questions: list[UnansweredQuestion | AnsweredQuestion]


class MinimalSearchResults(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    question_id: str
    question: str = Field(..., alias="question_str")
    retrieved_sources: list[MinimalSource]


class StudentSearchResults(BaseModel):
    search_results: list[MinimalSearchResults]
    k: int

class MinimalAnswer(MinimalSearchResults):
    answer: str

class StudentSearchResultsAndAnswer(StudentSearchResults):
    search_results: List[MinimalAnswer]