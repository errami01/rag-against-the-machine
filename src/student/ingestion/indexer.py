from pathlib import Path

from tqdm import tqdm

from student.ingestion.chunker import Chunker
from student.ingestion.loader import discover_files
from student.utils.json import save_json
from student.retrieval.bm25_index import BM25Indexer


class Indexer:

    def index(
        self,
        max_chunk_size: int = 2000,
    ) -> None:
        repo_path = "data/raw/vllm-0.10.1"
        files = discover_files(
            Path(repo_path)
        )

        chunker = Chunker(
            max_chunk_size
        )

        chunks = []
        for file in tqdm(files):
            try:
                chunks.extend(
                    chunker.chunk_file(
                        file
                    )
                )
            except Exception as exc:
                print(
                    f"Failed: {file}: {exc}"
                )

        save_json(
            "data/processed/chunks/chunks.json",
            [
                chunk.model_dump()
                for chunk in chunks
            ],
        )

        BM25Indexer().build(
            chunks,
            "data/processed/bm25/index",
        )

        print(
            f"Created {len(chunks)} chunks"
            f"\nIngestion complete! Indices saved under data/processed/"
        )