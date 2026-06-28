from student.generation.prompts import ANSWER_PROMPT
from student.generation.qwen import QwenModel
from student.retrieval.search import SearchEngine
from functools import lru_cache

def build_context(chunks, max_chars: int = 8000) -> str:

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

    def __init__(self) -> None:
        self.search_engine = (SearchEngine())

        self.llm = QwenModel()

    
    def answer(self, question: str, k: int = 5) -> str:

        chunks = (self.search_engine.search(question, k = k))

        context = build_context(chunks)

        prompt = build_prompt(question, context)
        print(f"Prompt: {prompt}")
        print("End of prompt")
        return self.llm.generate(prompt)