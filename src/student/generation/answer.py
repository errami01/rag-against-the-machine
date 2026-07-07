from student.generation.prompts import ANSWER_PROMPT
from student.generation.factory import BackendFactory
from student.retrieval.search import SearchEngine
from functools import lru_cache
from typing import List
from student.models.chunk import Chunk


def build_context(chunks: List[Chunk], max_chars: int = 2000) -> str:
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

    current_size = 0

    for chunk in chunks:

        text = (
            f"File: {chunk.file_path}\n"
            f"{chunk.text}\n"
        )

        if (current_size + len(text) > max_chars):
            break

        context_parts.append(text)

        current_size += len(text)

    return "\n\n".join(context_parts)


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

        context = build_context(chunks)

        prompt = build_prompt(question, context)
        try:
            response = self.llm.generate(prompt)
        except Exception as e:
            print(f"[LLM ERROR] {e}")
            response = "Error generating answer"
        return response
