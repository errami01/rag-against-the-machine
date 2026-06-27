from student.models import Chunk
from student.utils.json import load_json


class ChunkLookup:

    def __init__(self) -> None:

        raw = load_json("data/processed/chunks/chunks.json")

        self.lookup = {}

        for chunk in raw:

            chunk = Chunk.model_validate(chunk)

            key = (
                chunk.file_path,
                chunk.first_character_index,
                chunk.last_character_index,
            )

            self.lookup[key] = chunk

    def get(self, file_path: str, first: int, last: int) -> Chunk | None:

        return self.lookup.get((file_path, first, last))