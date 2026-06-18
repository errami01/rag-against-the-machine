from pydantic import BaseModel


class Source(BaseModel):
    file_path: str

    first_character_index: int
    last_character_index: int