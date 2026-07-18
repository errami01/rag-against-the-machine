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
    """An automated evaluation processor for running batch searches over
    a RAG dataset.

    This class loads a specified evaluation dataset, processes each
    question through a search engine pipeline to retrieve relevant
    text chunks, map their precise source character boundaries, and
    exports the final aggregated results to a JSON file.
    """

    def run(
        self,
        dataset_path: str,
        save_path: str,
        k: int = 10,
        rerank: bool = True,
    ) -> None:
        """Executes the batch search pipeline across all questions in the
        dataset.

        Iterates through the dataset questions, extracts the top-K relevant
        text chunks using a vector search engine, maps those chunks to
        metadata-rich sources, and saves the output configuration to disk.

        Args:
            dataset_path: The filesystem path or identifier of the dataset to
            load. save_path: The target filesystem path where the JSON results
            should be written.
            k: The maximum number of relevant documents or chunks to retrieve
            per question. Defaults to 10.

        Raises:
            OSError: If creating directories or writing the save file fails.
        """
        dataset = load_dataset(dataset_path)

        engine = SearchEngine(rerank=rerank)

        results: list[MinimalSearchResults] = []
        dataset_name = Path(dataset_path).stem
        for question in tqdm(dataset.rag_questions, desc="Searching"):

            chunks = engine.search(question.question, k=k, dataset_name=dataset_name)

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

        output = StudentSearchResults(
            search_results=results,
            k=k,
        )
        file_name = Path(save_path).name
        if not file_name.endswith(".json"):
            file_name = Path(dataset_path).name
            save_path = f"{save_path}/{file_name}"

        save_json(
            save_path,
            output.model_dump(by_alias=True),
        )

        print(
            f"Saved {len(results)} results to {save_path}"
        )
