from pathlib import Path

from tqdm import tqdm

from student.generation.answer import (
    build_prompt,
    build_context,
)
from student.generation.factory import BackendFactory
from student.models.dataset import (
    MinimalAnswer,
    StudentSearchResultsAndAnswer,
    MinimalSource,
)
from student.retrieval.chunk_lookup import ChunkLookup
from student.retrieval.search_results_loader import load_search_results
from student.utils.json import save_json


class DatasetAnswerer:
    """An automated processing hub for generating batch answers from search
      hits.

    This engine loads pre-computed search outputs, retrieves full text blocks
    from cache coordinates, builds prompt contexts, and flushes generated LLM
      responses to disk.
    """

    def run(
        self,
        search_results_path: str,
        save_path: str,
        backend: str = "transformers",
    ) -> None:
        """Run batch inference over a saved manifest of search result hits.

        Processes question objects sequentially, reconstructs their text
          content using source coordinate lookups, merges fragments into
            prompt structures, and updates the output schema with completed
              predictions.

        Args:
            search_results_path: The file path to the saved query search JSON.
            save_path: The target path where generated responses are stored.
            backend: The target model framework provider identifier string.
              Defaults to "transformers".

        Raises:
            OSError: If reading input files or writing output binaries fails.
            ValidationError: If data properties break schema definitions.
        """
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

            context, used_chunks = build_context(chunks)

            prompt = (
                build_prompt(
                    result.question,
                    context,
                )
            )

            answer = llm.generate(prompt)
            used_sources = [
                MinimalSource(
                    file_path=chunk.file_path,
                    first_character_index=chunk.first_character_index,
                    last_character_index=chunk.last_character_index,
                )
                for chunk in used_chunks
            ]

            answers.append(
                MinimalAnswer(
                    question_id=result.question_id,
                    question=result.question,
                    retrieved_sources=used_sources,
                    answer=answer,
                )
            )
        output = (
            StudentSearchResultsAndAnswer(
                search_results=answers,
                k=results.k,
            )
        )
        file_name = Path(save_path).name
        if not file_name.endswith(".json"):
            file_name = Path(search_results_path).name
            save_path = f"{save_path}/{file_name}"
        save_json(
            f"{save_path}",
            output.model_dump(),
        )

        print(
            f"Saved answers to {save_path}"
        )
