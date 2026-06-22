import bm25s

from student.models import Chunk
from student.retrieval.tokenizer import tokenize
from student.utils.json import load_json


class SearchEngine:

    def __init__(self) -> None:

        self.retriever = bm25s.BM25.load(
            "data/processed/bm25/index"
        )

        raw_chunks = load_json(
            "data/processed/chunks/chunks.json"
        )

        self.chunks = [
            Chunk.model_validate(chunk)
            for chunk in raw_chunks
        ]

    def search(
        self,
        query: str,
        k: int = 5,
    ) -> list[Chunk]:

        query_tokens = tokenize(query)

        results, scores = (
            self.retriever.retrieve(
                [query_tokens],
                k=k,
            )
        )
        
        indices = results[0]

        return [
            self.chunks[index]
            for index in indices
        ]