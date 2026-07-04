import fire
from student.ingestion.indexer import (Indexer)
from student.models import Chunk
from student.retrieval.search import (SearchEngine)
from student.retrieval.search_dataset import DatasetSearcher
from student.generation.answer import AnswerService
from student.generation.answer_dataset import DatasetAnswerer
from student.evaluation.evaluator import Evaluator
import time
import json


class CLI:
    def test_model(self) -> None:
        extensions = []
        with open("data/datasets/AnsweredQuestions/dataset_code_public.json", "r") as f:
            data = json.load(f)
        for question in data["rag_questions"]:
            for source in question["sources"]:
                extensions.append(source["file_path"].split(".")[-1])
        print(set(extensions))

    def index(self, max_chunk_size) -> None:
        Indexer().index(max_chunk_size)

    def search(self, query: str, k: int = 1) -> None:

        engine = SearchEngine()
        try:
            results = engine.search(query,k)
        except Exception as e:
            print(f"Error occurred while searching: {e}")
            return

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

    def answer(self,question: str,k: int = 5, backend: str = "transformers") -> None:
        response = AnswerService(backend=backend).answer(question,k=k)
        print(response)

    def answer_dataset(
        self,
        search_results_path: str,
        save_path: str,
        backend: str = "transformers",
    ) -> None:

        DatasetAnswerer().run(
            search_results_path,
            save_path,
        )

    def evaluate(
        self,
        student_answer_path: str,
        dataset_path: str,
        k: int = 10,
    ) -> None:

        Evaluator().evaluate(
            student_answer_path,
            dataset_path,
            k,
        )
if __name__ == "__main__":
    # 1. Start the timer
    start_time = time.perf_counter()
    # try:
    fire.Fire(CLI)
    # except Exception as e:
    #     print(f"[CLI ERROR] {e}")
    # 2. Stop the timer
    end_time = time.perf_counter()

    # 3. Calculate execution time
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.6f} seconds")
