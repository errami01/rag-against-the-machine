from student.generation.prompts import ANSWER_PROMPT
from student.generation.factory import BackendFactory 
from student.retrieval.search import SearchEngine
from functools import lru_cache

def build_context(chunks, max_chars: int = 4000) -> str:

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

    return ANSWER_PROMPT.format(
        context=context,
        question=question,
    )
class AnswerService:

    def __init__(
        self,
        backend: str = "transformers",
    ) -> None:

        self.search_engine = SearchEngine()

        self.llm = BackendFactory.create(
            backend
        )
    
    def answer(self, question: str, k: int = 5) -> str:

        chunks = (self.search_engine.search(question, k = k))

        context = build_context(chunks)

        prompt = build_prompt(question, context)
        try:
            response = self.llm.generate(prompt)
        except Exception as e:
            print(f"[LLM ERROR] {e}")
            response = "Error generating answer"        
        return response