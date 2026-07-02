from tqdm import tqdm

from student.generation.answer import (
    build_prompt,
    build_context,
)
from student.generation.factory import BackendFactory 
from student.models.dataset import (
    MinimalAnswer,
    StudentSearchResults,
    StudentSearchResultsAndAnswer,
)
from student.retrieval.chunk_lookup import ChunkLookup
from student.retrieval.search_results_loader import load_search_results
from student.utils.json import save_json


class DatasetAnswerer:

    def run(
        self,
        search_results_path: str,
        save_path: str,
        backend: str = "transformers",
    ) -> None:

        results = load_search_results(
            search_results_path
        )

        lookup = ChunkLookup()

        llm = BackendFactory.create(backend)

        answers = []
        for result in tqdm(
            results.search_results,
            desc="Answering",
        ):

            chunks = []

            for source in result.retrieved_sources:

                chunk = lookup.get(
                    source.file_path,
                    source.first_character_index,
                    source.last_character_index,
                )

                if chunk is not None:
                    chunks.append(chunk)

            context = build_context(chunks)

            prompt = (
                build_prompt(
                    result.question,
                    context,
                )
            )

            answer = llm.generate(prompt)

            answers.append(
                MinimalAnswer(
                    question_id=result.question_id,
                    question=result.question,
                    retrieved_sources=result.retrieved_sources,
                    answer=answer,
                )
            )
        output = (
            StudentSearchResultsAndAnswer(
                search_results=answers,
                k=results.k,
            )
        )

        save_json(
            save_path,
            output.model_dump(),
        )

        print(
            f"Saved answers to {save_path}"
        )