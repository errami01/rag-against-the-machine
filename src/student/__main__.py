import fire
from student.ingestion.indexer import (Indexer)
from student.models import Chunk
from student.retrieval.search import (SearchEngine)
from student.retrieval.search_dataset import DatasetSearcher
from student.generation.answer import AnswerService

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

    def index(self, max_chunk_size) -> None:
        Indexer().index(max_chunk_size)

    def search(self, query: str, k: int = 1) -> None:

        engine = SearchEngine()

        results = engine.search(query,k)

        for i, chunk in enumerate(results, start=1):
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
            # print(chunk.text[:500])

    def search_dataset(
        self,
        dataset_path: str,
        save_path: str,
        k: int = 10,
    ) -> None:
        DatasetSearcher().run(
            dataset_path=dataset_path,
            save_path=save_path,
            k=k,
        )
    def stats(self) -> None:
        from student.utils.json import load_json

        chunks = load_json(
            "data/processed/chunks/chunks.json"
        )

        print(f"Chunks: {len(chunks)}")
    def answer(self,question: str,k: int = 5) -> None:
        response = AnswerService().answer(question,k=k)
        print(response)

if __name__ == "__main__":
    fire.Fire(CLI)
