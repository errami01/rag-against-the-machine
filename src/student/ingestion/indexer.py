from pathlib import Path

from tqdm import tqdm

from student.ingestion.chunker import Chunker
from student.ingestion.loader import discover_files
from student.utils.json import save_json
from student.retrieval.bm25_index import BM25Indexer

class Indexer:
    """The central orchestration engine for the repository ingestion pipeline.

    This class coordinates the end-to-end processing of a source code or 
    documentation repository, transforming raw file trees into downstream 
    retrieval artifacts for the RAG search system.
    """

    def index(
        self,
        max_chunk_size: int = 2000,
    ) -> None:
        """Executes the ingestion, chunking, and lexical indexing pipeline.

        Crawls the designated raw repository path to discover supported source files, 
        processes each file sequentially through a size-constrained chunker, handles 
        runtime formatting exceptions gracefully, flushes the verified chunks to a 
        JSON manifest, and compiles a sparse BM25 search index.

        Args:
            max_chunk_size: The character ceiling configured for the file splitter. 
              Passed directly down to the internal chunking strategy. Defaults to 2000.

        Raises:
            OSError: If reading files or writing compiled artifacts to the output 
              directories (`data/processed/...`) fails.
        """
        repo_path = "data/raw/vllm-0.10.1"
        try:
            files = discover_files(
                Path(repo_path)
            )
        except Exception as e:
            raise e


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
