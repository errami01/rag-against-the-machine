import bm25s
from student.models import Chunk
from student.retrieval.tokenizer import tokenize
from student.utils.json import load_json
from student.retrieval.cache import SearchCache


class SearchEngine:

    def __init__(self) -> None:

        self.cache = SearchCache()
        self.retriever = bm25s.BM25.load("data/processed/bm25/index")
        raw_chunks = load_json("data/processed/chunks/chunks.json")
        self.chunks = [
            Chunk.model_validate(chunk)
            for chunk in raw_chunks
        ]

    def search(self, query: str, k: int = 5) -> list[Chunk]:
        
        cached_result = self.cache.get(query, k)
        if cached_result is not None:
            return cached_result

        query_tokens = list(tokenize(query))

        results, scores = (
            self.retriever.retrieve(
                [query_tokens],
                k=k,
            )
        )
        
        indices = results[0]
        chunks_result = [
            self.chunks[index]
            for index in indices
        ]
        self.cache.set(query, k, chunks_result)

        return chunks_result