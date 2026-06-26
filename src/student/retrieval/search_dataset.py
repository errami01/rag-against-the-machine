from pathlib import Path

from tqdm import tqdm

from student.datasets.loader import load_dataset
from student.models.dataset import (
    MinimalSearchResults,
    MinimalSource,
    StudentSearchResults,
)
from student.retrieval.search import SearchEngine
from student.utils.json import save_json


class DatasetSearcher:
    def run(
        self,
        dataset_path: str,
        save_path: str,
        k: int = 10,
    ) -> None:

        dataset = load_dataset(dataset_path)

        engine = SearchEngine()

        results: list[MinimalSearchResults] = []

        for question in tqdm(dataset.rag_questions, desc="Searching"):

            chunks = engine.search(question.question, k=k)

            sources = [
                MinimalSource(
                    file_path=chunk.file_path,
                    first_character_index=chunk.first_character_index,
                    last_character_index=chunk.last_character_index,
                )
                for chunk in chunks
            ]

            results.append(
                MinimalSearchResults(
                    question_id=question.question_id,
                    question=question.question,
                    retrieved_sources=sources,
                )
            )

        output = StudentSearchResults(search_results=results, k=k)

        save_path = Path(save_path)

        save_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        save_json(save_path, output.model_dump())

        print(f"Saved {len(results)} results to {save_path}")