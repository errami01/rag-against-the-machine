import fire
from student.ingestion.indexer import (Indexer)
from student.models import Chunk
from student.retrieval.search import (SearchEngine)


class CLI:
    def test_model(self) -> None:
        chunk = Chunk(
            chunk_id="1",
            file_path="example.py",
            file_type="python",
            text="print('hello')",
            first_character_index=0,
            last_character_index=14,
        )

        print(chunk.model_dump_json(indent=2))

    def index(
        self,
        max_chunk_size,
    ) -> None:

        Indexer().index(
            max_chunk_size,
        )
    def search(self, query: str, k: int = 1) -> None:

        engine = SearchEngine()

        results = engine.search(
            query,
            k,
        )

        for i, chunk in enumerate(
            results,
            start=1,
        ):
            print()
            print(f"Rank {i}")
            print(
                f"File: {chunk.file_path}"
            )
            print(
                f"Range: "
                f"{chunk.first_character_index}"
                f"-"
                f"{chunk.last_character_index}"
            )
            print(chunk.text[:500])

    def stats(self) -> None:
        from student.utils.json import load_json

        chunks = load_json(
            "data/processed/chunks/chunks.json"
        )

        print(f"Chunks: {len(chunks)}")
if __name__ == "__main__":
    fire.Fire(CLI)
