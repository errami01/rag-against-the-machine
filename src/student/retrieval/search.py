import bm25s
from student.models import Chunk
from student.retrieval.tokenizer import tokenize
from student.utils.json import load_json
from student.retrieval.cache import SearchCache
# from flashrank import Ranker, RerankRequest
from student.retrieval.reranker import Reranker


class SearchEngine:
    """A hybrid RAG search pipeline combining lexical retrieval and neural
    reranking.

    This engine initializes an index infrastructure to handle incoming user
    queries.
    It fetches initial candidates using a lexical BM25 index, scores and
    sorts the candidates with a deep learning cross-encoder model, and
    manages a low-latency result cache layer.
    """

    def __init__(self, rerank: bool = True) -> None:
        """Initializes the search engine by loading pre-computed indexes and
        models.

        Sets up the response cache, loads the saved BM25 token index,
        validates the document source chunks, and prepares the neural
        reranking module.

        Raises:
            Exception: If structural data dependencies
            (the index or chunk binaries) cannot be located on disk,
            prompting the user to run the indexer.
        """
        try:
            self.cache = SearchCache()
            self.retriever = bm25s.BM25.load("data/processed/bm25/index")
            raw_chunks = load_json("data/processed/chunks/chunks.json")
            self.rerank = rerank
            if self.rerank:
                self.reranker = Reranker()
            self.chunks = [
                Chunk.model_validate(chunk)
                for chunk in raw_chunks
            ]
        except Exception as e:
            print(f"[SEARCH ENGINE INIT ERROR] {e}")
            raise Exception(
                "Please run the indexer before using the search engine."
            )

    def search(self, query: str, k: int = 5) -> list[Chunk]:
        """Execute a complete retrieval-and-rerank sequence for a query.

        Checks the internal cache first. If a cache miss occurs, tokenizes
        the query, retrieves the raw lexical candidates, re-scores them
        using a neural cross-encoder pipeline, and stores the top-K sorted
        responses in the cache.

        Args:
            query: The natural language search query string.
            k: The number of top-ranked document chunks to return.
            Defaults to 5.

        Returns:
            A list of verified Chunk data structures sorted by decreasing
            relevance.
        """

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
        candidates = [
            self.chunks[index]
            for index in indices
        ]
        if not self.rerank:
            self.cache.set(query, k, candidates)
            return candidates
        scores = self.reranker.rerank(
            query,
            [chunk.text for chunk in candidates]
        )

        ranked = sorted(
            zip(scores, candidates),
            key=lambda x: x[0],
            reverse=True
        )
        final_results = [
            chunk
            for _, chunk in ranked[:k]
        ]
        self.cache.set(query, k, final_results)

        return final_results
