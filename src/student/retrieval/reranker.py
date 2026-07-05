from sentence_transformers import CrossEncoder


class Reranker:
    """A cross-encoder model wrapper for reranking retrieved documents.

    This class handles the initialization and inference of a cross-encoder
    model to score the semantic relevance of documents against a query. It
    utilizes a shared model instance to prevent redundant reloads across
    multiple initializations.
    """
    _MODEL = None

    def __init__(self) -> None:
        """Initializes the Reranker with a cross-encoder model.

        Loads the default MS-MARCO MiniLM model if it has not been
        initialized yet.
        """
        # Fixed: Use Reranker._MODEL to properly manage the shared class
        # variable
        if Reranker._MODEL is None:
            Reranker._MODEL = CrossEncoder(
                "cross-encoder/ms-marco-MiniLM-L-6-v2"
            )

        self.model = Reranker._MODEL

    def rerank(
        self,
        query: str,
        documents: list[str],
    ) -> list[float]:
        """Calculates relevance scores for a list of documents against a
        query.

        Pairs the query with each document and feeds them into the
        cross-encoder to get a prediction score. Higher scores indicate
        higher relevance.

        Args:
            query: The search query string.
            documents: A list of candidate document strings to be reranked.

        Returns:
            A list of floating-point relevance scores corresponding to each
            document.
        """
        pairs = [
            (query, document)
            for document in documents
        ]

        return self.model.predict(pairs).tolist()
