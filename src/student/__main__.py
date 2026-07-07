import fire
from student.ingestion.indexer import (Indexer)
from student.retrieval.search import (SearchEngine)
from student.retrieval.search_dataset import DatasetSearcher
from student.generation.answer import AnswerService
from student.generation.answer_dataset import DatasetAnswerer
from student.evaluation.evaluator import Evaluator
from student.utils.json import load_json
import time
import json
from pathlib import Path
from student.models.dataset import (
    MinimalSearchResults,
    MinimalSource,
)


class CLI:
    """Command-line interface commands for executing the RAG pipeline.

    Provides user-facing hooks to index files, execute interactive or batch
    searches, compute metrics, generate model answers, and run evaluation
    suites on submission datasets.
    """

    def test_model(self) -> None:
        """Inspect the public dataset to isolate source file extensions.

        Reads the local answered questions JSON configuration file and prints
        a distinct set of all file extensions present within the grounding
        sources.
        """
        extensions = []
        with open(
            "data/datasets/AnsweredQuestions/dataset_code_public.json", "r"
        ) as f:
            data = json.load(f)
        for question in data["rag_questions"]:
            for source in question["sources"]:
                extensions.append(source["file_path"].split(".")[-1])
        print(set(extensions))

    def index(self, max_chunk_size: int) -> None:
        """Build the global text chunk collection and lexical indices.

        Delegates to the Indexer engine to crawl the repository tree, split
        files into size-constrained fragments, and update the database index.

        Args:
            max_chunk_size: The character limit constraint for each text chunk.
        """
        try:
            Indexer().index(max_chunk_size)
        except Exception as e:
            print(e)
            return

    def search(self, query: str, k: int = 5) -> None:
        """Execute a query search against the document index and print results.

        Fetches the top-K matching text fragments via the retrieval engine
        and displays rank details alongside absolute coordinate boundaries.

        Args:
            query: The text search string.
            k: The maximum number of relevant documents to retrieve.
              Defaults to 1.
        """
        try:
            # 1. Define your target folder and file path
            output_dir = Path("data/output/single_search_results")
            file_path = output_dir / "single_search_results.json"
            # 2. Automatically create parent directories if missing
            output_dir.mkdir(parents=True, exist_ok=True)
            engine = SearchEngine()
            chunks = engine.search(query, k)
            result: MinimalSearchResults = MinimalSearchResults(
                question_id="single_search",
                question=query,
                retrieved_sources=[
                    MinimalSource(
                        file_path=chunk.file_path,
                        first_character_index=chunk.first_character_index,
                        last_character_index=chunk.last_character_index,
                    )
                    for chunk in chunks
                ]
            )
            file_path.write_text(
                result.model_dump_json(indent=4), encoding="utf-8")
        except Exception as e:
            print(f"Error occurred while searching: {e}")
            return

        for i, chunk in enumerate(chunks, start=1):
            print()
            print(f"Rank {i}")
            print(f"File: {chunk.file_path}")
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
        """Run batch search loops over an evaluation dataset file.

        Extracts candidate chunks for every question present in the dataset
        and exports the structured footprint directly to a JSON destination.

        Args:
            dataset_path: The file path to the target query dataset.
            save_path: The destination path where search matrices are written.
            k: Retrieval ceiling allocated per query instance. Defaults to 10.
        """
        try:
            DatasetSearcher().run(
                dataset_path=dataset_path,
                save_path=save_path,
                k=k,
            )
        except Exception as e:
            print(e)
            return

    def stats(self) -> None:
        """Calculate and log processing statistics for the current index.

        Loads the active chunk configuration collection and prints out the
        total volume of items managed inside the global data matrix.
        """

        chunks = load_json("data/processed/chunks/chunks.json")
        print(f"Chunks: {len(chunks)}")

    def answer(
        self, question: str, k: int = 5, backend: str = "transformers"
    ) -> None:
        """Generate a contextual solution for a standalone natural query.

        Submits a query to the answer coordinator pipeline and flushes out the
        resulting model response text directly to the console window.

        Args:
            question: The natural language statement submitted for inference.
            k: The retrieval depth passed down to the pipeline. Defaults to 5.
            backend: The active inference infrastructure tag. Defaults to
              "transformers".
        """
        try:
            response = AnswerService(backend=backend).answer(question, k=k)
        except Exception as e:
            print(f"Answer Error: {e}")
            return
        print(response)

    def answer_dataset(
        self,
        search_results_path: str,
        save_path: str,
        backend: str = "transformers",
    ) -> None:
        """Process predictions over a batch file of compiled search hits.

        Passes previous search results to a batch processing component to
        synthesize individual answers and exports the outcome collection.

        Args:
            search_results_path: The location of the pre-computed results.
            save_path: The file target where completed predictions are written.
            backend: The target model backend platform identifier. Defaults to
              "transformers".
        """
        try:
            DatasetAnswerer().run(
                search_results_path,
                save_path,
            )
        except Exception as e:
            print(f"Answer dataset Error: {e}")

    def evaluate(
        self,
        student_answer_path: str,
        dataset_path: str,
        k: int = 10,
    ) -> None:
        """Evaluate a student submission against target ground-truth bounds.

        Triggers an evaluation calculation suite to score accuracy, reference
        overlap metrics, and context alignment characteristics.

        Args:
            student_answer_path: The path pointing to the student JSON output.
            dataset_path: The path to the gold-standard reference dataset.
            k: The top-K retrieval context validation limit. Defaults to 10.
        """
        try:
            Evaluator().evaluate(
                student_answer_path,
                dataset_path,
                k,
            )
        except Exception as e:
            print(f"Evaluation Error: {e}")
            return


if __name__ == "__main__":
    # 1. Start the timer
    start_time = time.perf_counter()
    try:
        fire.Fire(CLI)
    except Exception as e:
        print(f"[CLI ERROR] {e}")
    # 2. Stop the timer
    end_time = time.perf_counter()

    # 3. Calculate execution time
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.6f} seconds")
