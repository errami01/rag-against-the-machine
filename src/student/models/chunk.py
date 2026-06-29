from pydantic import BaseModel


class Chunk(BaseModel):
    chunk_id: str

    file_path: str
    file_type: str = "markdown"

    text: str

    first_character_index: int
    last_character_index: int
