import ast
import hashlib
from pathlib import Path

from student.models import Chunk


class PythonChunker:
    def __init__(
        self,
        max_chunk_size: int = 2000,
    ) -> None:
        self.max_chunk_size = max_chunk_size

    def chunk_file(self,path: Path) -> list[Chunk]:

        text = path.read_text(encoding="utf-8",errors="ignore",)

        tree = ast.parse(text)

        chunks: list[Chunk] = []

        for node in ast.walk(tree):
            if not isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                    ast.ClassDef,
                ),
            ):
                continue

            start_line = node.lineno
            end_line = node.end_lineno

            if end_line is None:
                continue

            lines = text.splitlines(
                keepends=True,
            )

            start_char = sum(
                len(line)
                for line in lines[: start_line - 1]
            )

            end_char = sum(
                len(line)
                for line in lines[:end_line]
            )

            chunk_text = text[
                start_char:end_char
            ]

            chunks.extend(
                self._split_large_chunk(
                    path,
                    chunk_text,
                    start_char,
                )
            )

        return chunks
    def _split_large_chunk(
        self,
        path: Path,
        text: str,
        start_offset: int,
    ) -> list[Chunk]:

        overlap = 200

        chunks: list[Chunk] = []

        current = 0

        while current < len(text):

            end = min(
                current + self.max_chunk_size,
                len(text),
            )

            chunk_text = text[current:end]

            absolute_start = (start_offset + current)

            absolute_end = (start_offset + end)

            chunk_id = hashlib.md5(
                (
                    str(path)
                    + str(absolute_start)
                ).encode()
            ).hexdigest()

            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    file_path=str(path),
                    file_type="python",
                    text=chunk_text,
                    first_character_index=absolute_start,
                    last_character_index=absolute_end,
                )
            )

            current += (self.max_chunk_size - overlap)

        return chunks