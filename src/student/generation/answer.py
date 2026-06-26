from student.generation.prompts import ANSWER_PROMPT
from student.generation.qwen import QwenModel
from student.models.chunk import Chunk
from student.retrieval.search import SearchEngine
from functools import lru_cache
import json
from pathlib import Path

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

    @lru_cache(maxsize=1024)
    def build_prompt(self, question: str, context: str) -> str:

        return ANSWER_PROMPT.format(
            context=context,
            question=question,
        )
    
    def answer(self, question: str, k: int = 5) -> str:

        cache_path = Path("data/processed/cache/search_cache.json")
        is_cached = False
        if cache_path.exists():
            with open(cache_path, "r") as f:
                cache_data = json.load(f)
                for entry in cache_data:
                    if entry["query"] == question and entry["k"] == k:
                        chunks = [
                            Chunk.model_validate(chunk)
                            for chunk in entry["chunks"]
                        ]
                        is_cached = True
        if not is_cached:
            chunks = self.search_engine.search(question, k = k)
        context = build_context(chunks)

        prompt = self.build_prompt(question, context)

        return self.llm.generate(prompt)