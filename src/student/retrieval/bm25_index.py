from pathlib import Path
import bm25s
from student.models import Chunk
from student.retrieval.tokenizer import tokenize


class BM25Indexer:
    """An index builder for creating and saving BM25 lexical search profiles.

    This class processes raw text chunks through a localized tokenization
      pipeline, compiles them into a term frequency matrix via the bm25s
        library, and flushes the resulting retrieval artifacts to disk for
          downstream query matching.
    """

    def build(
        self,
        chunks: list[Chunk],
        output_dir: str,
    ) -> None:
        """Constructs a BM25 index from text chunks and saves it to a
          directory.

        Extracts text from each chunk, passes it through the workspace
          tokenization rules, builds the sparse inverted index structure,
            and safely writes all
              compiled binaries to the chosen output directory.

        Args:
            chunks: A list of validated Chunk instances containing the raw
              source text.
            output_dir: The target filesystem directory where the index
              binaries should be stored.

        Raises:
            OSError: If creating the output directory directory or writing the
              index binaries to disk fails.
        """
        corpus = [
            tokenize(chunk.text)
            for chunk in chunks
        ]

        retriever = bm25s.BM25()

        retriever.index(corpus)

        Path(output_dir).mkdir(
            parents=True,
            exist_ok=True,
        )

        retriever.save(output_dir)
