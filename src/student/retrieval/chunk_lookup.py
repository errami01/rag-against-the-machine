from student.models import Chunk
from student.utils.json import load_json


class ChunkLookup:
    """An exact-match indexing map for retrieving pre-processed text chunks.

    This class loads raw chunks from disk, validates them into a structured
    schema, and indexes them into an in-memory dictionary using a composite
    key (file path, start index, and end index). This enables O(1)
    constant-time verification and lookup during evaluation or retrieval
    tasks.
    """

    def __init__(self) -> None:
        """Initializes the lookup map by parsing saved chunk files.

        Loads the global chunk repository and structures the lookup index
        around unique character boundary coordinates.
        """
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
        """Retrieves a specific chunk using its coordinate metadata.

        Args:
            file_path: The target filesystem or repository path of the source
            file.
            first: The character index denoting the start of the text chunk.
            last: The character index denoting the end of the text chunk.

        Returns:
            The matching verified Chunk object if found; otherwise, None.
        """
        return self.lookup.get((file_path, first, last))
