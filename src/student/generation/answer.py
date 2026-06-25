from student.generation.prompts import ANSWER_PROMPT
from student.generation.qwen import QwenModel
from student.retrieval.search import SearchEngine

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

class AnswerService:

    def __init__(self) -> None:
        self.search_engine = (SearchEngine())

        self.llm = QwenModel()
    
    def answer(self, question: str, k: int = 5) -> str:

        chunks = (self.search_engine.search(question, k = k))

        context = build_context(chunks)

        prompt = ANSWER_PROMPT.format(context=context, question=question)

        return self.llm.generate(prompt)