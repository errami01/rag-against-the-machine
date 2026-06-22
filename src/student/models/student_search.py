from pydantic import BaseModel
from typing import List
from src.student.models.search_result import MinimalSearchResults, MinimalAnswer


class StudentSearchResults(BaseModel):
    search_results: List[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(StudentSearchResults):
    search_results: List[MinimalAnswer]