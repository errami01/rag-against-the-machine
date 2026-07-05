from student.models import Chunk


class SearchCache:
    """An in-memory caching layer for tracking specific search query results.

    This class maintains an isolated, transient lookup dictionary mapping
    unique combinations of user queries and requested top-K thresholds to
    their pre-computed lists of text chunks.
    """

    def __init__(self) -> None:
        """Initializes an empty search cache map."""
        self._cache: dict[tuple[str, int], list[Chunk]] = {}

    def get(self, query: str, k: int) -> list[Chunk] | None:
        """Retrieves cached chunks for a specific query and top-K parameter
        combination.

        Args:
            query: The search query string.
            k: The exact number of retrieved documents requested for the
              search.

        Returns:
            A list of matching Chunk objects if a precise hit exists,
              otherwise None.
        """
        return self._cache.get((query, k))

    def set(self, query: str, k: int, chunks: list[Chunk]) -> None:
        """Stores a search result list tied to a query and its top-K
          constraint.

        Args:
            query: The search query string used to generate the results.
            k: The number of documents requested for this search sequence.
            chunks: The list of validated Chunk results to be cached.
        """
        self._cache[(query, k)] = chunks
