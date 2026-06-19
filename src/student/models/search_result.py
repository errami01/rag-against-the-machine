from pydantic import BaseModel

from student.models.source import Source


class SearchResult(BaseModel):
    question_id: str

    retrieved_sources: list[Source]
