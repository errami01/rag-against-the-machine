from pathlib import Path

from student.ingestion.markdown_chunker import (MarkdownChunker)
from student.ingestion.python_chunker import (PythonChunker)
from student.models import Chunk

class Chunker:

    def __init__(self, max_chunk_size: int = 2000) -> None:

        self.python_chunker = (
            PythonChunker(
                max_chunk_size,
            )
        )

        self.markdown_chunker = (
            MarkdownChunker(
                max_chunk_size,
            )
        )

    def chunk_file(self, path: Path) -> list[Chunk]:

        if path.suffix == ".py":
            return (
                self.python_chunker
                .chunk_file(path)
            )

        return (
            self.markdown_chunker
            .chunk_file(path)
        )