from student.models import Chunk


class SearchCache:

    def __init__(self) -> None:
        self._cache: dict[tuple[str, int], list[Chunk]] = {}

    def get(self, query: str, k: int) -> list[Chunk] | None:
        return self._cache.get((query, k))

    def set(self, query: str, k: int, chunks: list[Chunk]) -> None:
        self._cache[(query, k)] = chunks