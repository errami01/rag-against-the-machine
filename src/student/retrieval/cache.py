from student.models import Chunk
from student.utils.json import save_json

class SearchCache:

    def __init__(self) -> None:
        self._cache: dict[tuple[str, int], list[Chunk]] = {}

    def get(self, query: str, k: int) -> list[Chunk] | None:
        return self._cache.get((query, k))

    def set(self, query: str, k: int, chunks: list[Chunk]) -> None:
        self._cache[(query, k)] = chunks
        json_cache = [
            {
                "query": query,
                "k": k,
                "chunks": [chunk.model_dump() for chunk in chunks],
            }
        ]
        save_json("data/processed/cache/search_cache.json", json_cache)