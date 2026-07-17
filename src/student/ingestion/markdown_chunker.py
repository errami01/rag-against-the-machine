import hashlib
import re
from pathlib import Path

from student.models import Chunk
from student.utils.project_root import get_project_root

HEADER_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
PARAGRAPH_PATTERN = re.compile(r"\n\s*\n")
SENTENCE_PATTERN = re.compile(r"(?<=[.!?])\s+")


class MarkdownChunker:
    """
    Markdown chunker that guarantees every emitted chunk
    is <= max_chunk_size characters (including metadata).

    Split order:

        Headers
            ↓
        Paragraphs
            ↓
        Sentences
            ↓
        Character windows

    The final emitted chunk NEVER exceeds max_chunk_size.
    """

    def __init__(
        self,
        max_chunk_size: int = 2000,
        overlap: int = 400,
    ):
        """Initialize the hierarchical text chunker.

        Args:
            max_chunk_size: The maximum allowed character length for
              any unified chunk, including injected metadata headers.
              Defaults to 2000.
            overlap: The character window fallback constraint used when
              performing hard character-level cuts across oversized
              fragments. Defaults to 400.
        """
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    #########################################################
    # Public
    #########################################################

    def chunk_file(self, path: Path) -> list[Chunk]:
        text = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )
        """Parse a document file hierarchically based on structural headings.

        Tracks Markdown header boundaries to isolate distinct nested
        contexts. It dynamically maps parent-child heading relationships
        up to level 6 and splits text sections into metadata-annotated
        chunks. If a file contains no headers, it treats the entire text
        content as a single raw section block.

        Args:
            path: The pathlib.Path pointing to the document file on disk.

        Returns:
            A list of structural Chunk objects containing context text.
        """
        matches = list(HEADER_PATTERN.finditer(text))
        path = path.relative_to(f"{get_project_root()}")
        if not matches:
            return self._split_section(
                path,
                text,
                0,
                [],
            )

        chunks = []

        # Intro text before first heading
        if matches[0].start() > 0:
            intro = text[: matches[0].start()]
            if intro.strip():
                chunks.extend(
                    self._split_section(
                        path,
                        intro,
                        0,
                        ["Introduction"],
                    )
                )

        current_headers = [""] * 6

        for i, match in enumerate(matches):

            start = match.start()

            end = (
                matches[i + 1].start()
                if i + 1 < len(matches)
                else len(text)
            )

            level = len(match.group(1))
            title = match.group(2).strip()

            current_headers[level - 1] = title

            for j in range(level, 6):
                current_headers[j] = ""

            context = [
                h
                for h in current_headers[:level]
                if h
            ]

            section = text[start:end]

            chunks.extend(
                self._split_section(
                    path,
                    section,
                    start,
                    context,
                )
            )

        return chunks

    #########################################################
    # Helpers
    #########################################################

    def _metadata(self, path: Path, context: list[str]) -> str:
        """Format the context hierarchy into a metadata prefix string.

        Args:
            path: The source file Path context.
            context: An ordered list of ancestor heading names leading
              down to the current active text scope.

        Returns:
            A string containing formatted key-value labels if context
            exists; otherwise an empty string.
        """
        if not context:
            return ""

        return (
            f"File: {path.name}\n"
            f"Section: {' > '.join(context)}\n\n"
        )

    def _fits(self, body: str, metadata: str) -> bool:
        """Verify if the total length of a segment respects size constraints.

        Args:
            body: The text content under validation.
            metadata: The metadata prefix sequence to attach.

        Returns:
            True if the combined character footprint is equal to or less
            than the maximum size threshold; otherwise False.
        """
        return len(metadata) + len(body) <= self.max_chunk_size

    #########################################################
    # Section
    #########################################################

    def _split_section(
        self,
        path: Path,
        section: str,
        offset: int,
        context: list[str],
    ) -> list[Chunk]:
        """Process an isolated heading section down into paragraph blocks.

        If the entire section along with its metadata prefix fits within
        the configured character budget, it generates a single chunk.
        Otherwise, it splits the text by paragraph boundaries and merges
        paragraphs sequentially up to the size limit.

        Args:
            path: The source file Path context.
            section: The raw text snippet captured inside the context.
            offset: The global starting character position of this
              section within the root file.
            context: Ancestor headings sequence tracking document depth.

        Returns:
            A list of parsed structural Chunk objects.
        """
        metadata = self._metadata(path, context)

        if self._fits(section, metadata):
            return [
                self._make_chunk(
                    path,
                    metadata + section,
                    offset,
                    offset + len(section),
                )
            ]

        paragraphs = PARAGRAPH_PATTERN.split(section)

        chunks = []

        current = ""
        current_start = 0

        running_offset = 0

        for paragraph in paragraphs:

            paragraph = paragraph.strip()

            if not paragraph:
                running_offset += 2
                continue

            candidate = (
                current + "\n\n" + paragraph
                if current
                else paragraph
            )

            if self._fits(candidate, metadata):

                if not current:
                    current_start = running_offset

                current = candidate

            else:

                if current:

                    chunks.append(
                        self._make_chunk(
                            path,
                            metadata + current,
                            offset + current_start,
                            offset + current_start + len(current),
                        )
                    )

                if self._fits(paragraph, metadata):

                    current = paragraph
                    current_start = running_offset

                else:

                    chunks.extend(
                        self._split_large_paragraph(
                            path,
                            paragraph,
                            offset + running_offset,
                            metadata,
                        )
                    )

                    current = ""

            running_offset += len(paragraph) + 2

        if current:

            chunks.append(
                self._make_chunk(
                    path,
                    metadata + current,
                    offset + current_start,
                    offset + current_start + len(current),
                )
            )

        return chunks

    def _split_large_paragraph(
        self,
        path: Path,
        paragraph: str,
        offset: int,
        metadata: str,
    ) -> list[Chunk]:
        """Partition an oversized paragraph block using sentence boundaries.

        Aggregates sentences sequentially while keeping combined text and
        metadata under the configured character ceiling.

        Args:
            path: The source file Path context.
            paragraph: The text block that breached chunk limits.
            offset: The absolute index position tracking paragraph start.
            metadata: Pre-formatted file and section tracking headers.

        Returns:
            A list of granular, sentence-aggregated Chunk entries.
        """
        sentences = SENTENCE_PATTERN.split(paragraph)

        chunks = []

        current = ""
        current_start = 0

        running_offset = 0

        for sentence in sentences:

            candidate = (
                current + " " + sentence
                if current
                else sentence
            )

            if self._fits(candidate, metadata):

                if not current:
                    current_start = running_offset

                current = candidate

            else:

                if current:

                    chunks.append(
                        self._make_chunk(
                            path,
                            metadata + current,
                            offset + current_start,
                            offset + current_start + len(current),
                        )
                    )

                if self._fits(sentence, metadata):

                    current = sentence
                    current_start = running_offset

                else:

                    chunks.extend(
                        self._hard_split(
                            path,
                            sentence,
                            offset + running_offset,
                            metadata,
                        )
                    )

                    current = ""

            running_offset += len(sentence) + 1

        if current:

            chunks.append(
                self._make_chunk(
                    path,
                    metadata + current,
                    offset + current_start,
                    offset + current_start + len(current),
                )
            )

        return chunks

    #########################################################
    # Final fallback
    #########################################################

    def _hard_split(
        self,
        path: Path,
        text: str,
        offset: int,
        metadata: str,
    ) -> list[Chunk]:

        chunks = []

        available = self.max_chunk_size - len(metadata)

        start = 0

        while start < len(text):

            end = min(
                len(text),
                start + available,
            )

            piece = text[start:end]

            chunks.append(
                self._make_chunk(
                    path,
                    metadata + piece,
                    offset + start,
                    offset + end,
                )
            )

            if end == len(text):
                break

            start = max(
                end - self.overlap,
                start + 1,
            )

        return chunks

    def _make_chunk(
        self,
        path: Path,
        text: str,
        start: int,
        end: int,
    ) -> Chunk:

        # Safety guarantee
        assert (
            len(text) <= self.max_chunk_size
        ), f"Chunk size is {len(text)} (> {self.max_chunk_size})"

        chunk_id = hashlib.sha256(
            f"{path}:{start}:{end}".encode()
        ).hexdigest()

        return Chunk(
            chunk_id=chunk_id,
            file_path=str(path),
            file_type="markdown",
            text=text,
            first_character_index=start,
            last_character_index=end,
        )
