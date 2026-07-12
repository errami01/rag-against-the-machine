from student.generation.prompts import ANSWER_PROMPT
from student.generation.factory import BackendFactory
from student.retrieval.search import SearchEngine
from functools import lru_cache
from typing import List, Tuple
from student.models.chunk import Chunk
from student.models.dataset import (
    MinimalSource, MinimalAnswer, StudentSearchResultsAndAnswer)
from student.utils.json import save_json
import json


def build_context(
        chunks: List[Chunk], max_chars: int = 4000
        ) -> Tuple[str, List[Chunk]]:
    """Assemble a combined context string from document chunks.

    Iterates through retrieved text chunks, formats them with their clear
      source
    file headers, and chains them together up to a strict maximum character
    budget limit.

    Args:
        chunks: An iterable collection of verified Chunk data models.
        max_chars: The maximum length cutoff parameter allowed for the unified
          string layout. Defaults to 2000.

    Returns:
        A combined context string separated by double line breaks.
    """
    context_parts = []
    used_chunks = []
    current_size = 0

    for chunk in chunks:

        text = (
            f"Source ID: {chunk.chunk_id}\n"
            f"{chunk.text}\n"
        )

        if (current_size + len(text) > max_chars):
            break

        context_parts.append(text)
        used_chunks.append(chunk)
        current_size += len(text)

    return "\n\n".join(context_parts), used_chunks


@lru_cache(maxsize=1024)
def build_prompt(question: str, context: str) -> str:
    """Construct a standardized LLM inference prompt sequence.

    Injects the packed reference context payload along with the input query
    into a predefined baseline instruction template layout.

    Args:
        question: The natural language search query string.
        context: The text string containing matched reference document blocks.

    Returns:
        The formatted prompt ready to be processed by an inference model.
    """
    return ANSWER_PROMPT.format(
        context=context,
        question=question,
    )


class AnswerService:
    """A business logic coordinator for answering standalone queries.

    This service connects individual system components together by executing
    searches, organizing extracted text, and routing instructions to an
      inference
    backend to resolve individual requests.
    """

    def __init__(
        self,
        backend: str = "transformers",
    ) -> None:
        """Initialize the coordination service and create model connections.

        Args:
            backend: The identifier tag mapping the specific active model
              engine stack configuration. Defaults to "transformers".
        """
        self.search_engine = SearchEngine()

        self.llm = BackendFactory.create(
            backend
        )

    def answer(self, question: str, k: int = 5) -> str:
        """Generate a contextual answer for an input question.

        Fetches top-K document blocks from the index, reduces fragments into a
        budget-aligned text sequence, builds the localized target prompt, and
        requests inference from the backend gateway.

        Args:
            question: The natural language query submitted for processing.
            k: The document chunk retrieval window limit. Defaults to 5.

        Returns:
            The raw textual solution produced by the language model, or a
              fallback error string if inference fails.
        """
        chunks = (self.search_engine.search(question, k=k))
        answers: list[MinimalAnswer] = []
        save_path = "data/output/answers/single_answer.json"
        context, used_chunks = build_context(chunks)

        prompt = build_prompt(question, context)
        try:
            response = self.llm.generate(prompt)
        except Exception as e:
            raise Exception(f"LLM ERROR: {e}")
        try:
            res = response[
                response.index("{"): len(response) - response[::-1].index('}')
                ]
            res_dict = json.loads(res)
        except Exception:
            res_dict = {"answer": "No answer", "source_id": "No answer"}
        try:
            used_chunks = [
                chunk for chunk in used_chunks
                if chunk.chunk_id == res_dict.get('source_id')]
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
                    question_id="single_answer",
                    question_str=question,
                    retrieved_sources=used_sources,
                    answer=res_dict['answer'],
                )
            )
            output = (
                StudentSearchResultsAndAnswer(
                    search_results=answers,
                    k=k
                )
            )

            save_json(
                save_path,
                output.model_dump(),
            )

            print(
                f"Saved answers to {save_path}"
            )
        except Exception as e:
            print(f"[LLM ERROR] {e}")
            response = "Error generating answer"
        return response
