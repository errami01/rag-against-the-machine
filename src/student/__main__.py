import fire
from student.ingestion.indexer import (Indexer)
from student.models import Chunk


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
        repo_path: str,
        max_chunk_size: int = 2000,
    ) -> None:

        Indexer().index(
            repo_path,
            max_chunk_size,
        )

if __name__ == "__main__":
    fire.Fire(CLI)
