from pydantic import BaseModel


class Chunk(BaseModel):
    """A data model representing a granular, extracted segment of a source
      document.

    This schema stores parsed text fragments alongside structural tracking
      metadata.
    It maintains character-level offsets to map the split text precisely back
      to its location in the original file, which is critical for source
        citation and evaluation in RAG pipelines.

    Attributes:
        chunk_id: A unique identifier generated for this text segment.
        file_path: The filesystem or repository path of the source document.
        file_type: The format or extension of the source file (e.g.,
          'markdown', 'python'). Defaults to "markdown".
        text: The raw textual contents extracted for indexing and retrieval.
        first_character_index: The starting 0-indexed character boundary of
          this segment within the source file.
        last_character_index: The ending 0-indexed character boundary of this
          segment within the source file.
    """
    chunk_id: str

    file_path: str
    file_type: str = "markdown"

    text: str

    first_character_index: int
    last_character_index: int
