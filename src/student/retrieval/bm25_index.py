from pathlib import Path
import bm25s
from student.models import Chunk
from student.retrieval.tokenizer import tokenize

class BM25Indexer:

    def build(
        self,
        chunks: list[Chunk],
        output_dir: str,
    ) -> None:

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