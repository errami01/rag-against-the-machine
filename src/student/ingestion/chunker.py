from pathlib import Path

from student.ingestion.markdown_chunker import (MarkdownChunker)
from student.ingestion.python_chunker import (PythonChunker)
from student.models import Chunk


class Chunker:
    """A polymorphic routing layer for handling multi-format file chunking.

    This class serves as a unified entry point for the text partitioning
      pipeline.
    It instantiates specialized format chunkers (Python and Markdown) and
      delegates incoming files to the appropriate chunking strategy based
      on file extensions.
    """

    def __init__(self, max_chunk_size: int = 2000) -> None:
        """Initializes the routing chunker and its underlying parser
        strategies.

        Args:
            max_chunk_size: The maximum allowed character footprint constraint
              passed directly to both sub-chunker engine instances. Defaults
              to 2000.
        """
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
        """Routes a file to its correct syntax-aware parser based on
        extension.

        Inspects the file suffix. Files ending in '.py' are handed off to the
        AST-driven Python chunker, while all other file formats fall back to
        hierarchical markdown structure segmentation.

        Args:
            path: The pathlib.Path pointing to the document file on disk.

        Returns:
            A list of schema-validated Chunk objects containing extracted
            and context-prepended text segments.
        """
        if path.suffix == ".py":
            return (
                self.python_chunker
                .chunk_file(path)
            )

        return (
            self.markdown_chunker
            .chunk_file(path)
        )
