from pydantic import BaseModel


class Answer(BaseModel):
    question_id: str
    answer: str
