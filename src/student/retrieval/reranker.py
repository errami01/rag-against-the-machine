from sentence_transformers import CrossEncoder


class Reranker:
    _MODEL = None
    def __init__(self) -> None:

        if self._MODEL is None:
            self._MODEL = CrossEncoder(
                "cross-encoder/ms-marco-MiniLM-L-6-v2"
            )

        self.model = self._MODEL

    def rerank(
        self,
        query: str,
        documents: list[str],
    ) -> list[float]:
        pairs = [
            (query, document)
            for document in documents
        ]

        return self.model.predict(pairs).tolist()