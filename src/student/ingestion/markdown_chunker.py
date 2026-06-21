import hashlib
import re
from pathlib import Path

from student.models import Chunk


HEADER_PATTERN = re.compile(r"^#{1,6}\s",re.MULTILINE)

class MarkdownChunker:

    def __init__(
        self,
        max_chunk_size: int = 2000,
    ) -> None:
        self.max_chunk_size = max_chunk_size

    def chunk_file(
        self,
        path: Path,
    ) -> list[Chunk]:

        text = path.read_text(encoding="utf-8", errors="ignore")
        matches = list(
            HEADER_PATTERN.finditer(text)
        )

        if not matches:
            return self._create_chunks(
                path,
                text,
                0
            )

        chunks: list[Chunk] = []

        for i, match in enumerate(matches):
            start = match.start()

            if i + 1 < len(matches):
                end = matches[i + 1].start()
            else:
                end = len(text)

            chunks.extend(
                self._create_chunks(
                    path,
                    text[start:end],
                    start,
                )
            )

        return chunks

    def _create_chunks(
        self,
        path: Path,
        text: str,
        offset: int,
    ) -> list[Chunk]:

        result: list[Chunk] = []

        current = 0

        overlap = 200

        while current < len(text):

            end = min(
                current + self.max_chunk_size,
                len(text),
            )

            chunk_text = text[current:end]

            chunk_id = hashlib.md5(
                (
                    str(path)
                    + str(offset + current)
                ).encode()
            ).hexdigest()

            result.append(
                Chunk(
                    chunk_id=chunk_id,
                    file_path=str(path),
                    file_type="markdown",
                    text=chunk_text,
                    first_character_index=offset
                    + current,
                    last_character_index=offset
                    + end,
                )
            )

            current += (
                self.max_chunk_size
                - overlap
            )

        return result