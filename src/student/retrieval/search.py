import bm25s
from student.models import Chunk
from student.retrieval.tokenizer import tokenize
from student.utils.json import load_json
from student.retrieval.cache import SearchCache
# from flashrank import Ranker, RerankRequest
from student.retrieval.reranker import Reranker

class SearchEngine:

    def __init__(self) -> None:
        try:
            self.cache = SearchCache()
            self.retriever = bm25s.BM25.load("data/processed/bm25/index")
            raw_chunks = load_json("data/processed/chunks/chunks.json")
            self.reranker = Reranker()
            self.chunks = [
                Chunk.model_validate(chunk)
                for chunk in raw_chunks
            ]
        except Exception as e:
            print(f"[SEARCH ENGINE INIT ERROR] {e}")
            raise Exception("Please run the indexer before using the search engine.")

    def search(
        self,
        query: str,
        k: int = 30,
    ) -> list[Chunk]:
        
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
        scores = self.reranker.rerank(
        query,
        [chunk.text for chunk in candidates],
    )

        ranked = sorted(
            zip(scores, candidates),
            key=lambda x: x[0],
            reverse=True,
        )
        final_results = [
            chunk
            for _, chunk in ranked[:k]
        ]
        self.cache.set(query, k, final_results)

        return final_results


    # 1. Initialize the lightweight CPU-optimized Reranker model
    # (e.g., 'ms-marco-MiniLM-L-4-v2' takes less than 30MB of memory and executes in milliseconds)

    # def search_with_reranking(self,query_text: str, k: int = 20) -> list[Chunk]:
    #     reranker_model = Ranker(model_name="ms-marco-MiniLM-L-12-v2")
    #     # --- STAGE 1: Fast BM25 Lookup ---
    #     query_tokens = list(tokenize(query_text))
        
    #     # Retrieve a slightly wider net (e.g., top 20) to ensure the answer is caught
    #     bm25_results, bm25_indices = (
    #         self.retriever.retrieve(
    #             [query_tokens],
    #             k=k,
    #         )
    #     )
        
    #     # Flatten results to match standard list format
    #     indices = bm25_results[0]
    #     matched_chunks = [
    #         self.chunks[index]
    #         for index in indices
    #     ]
        
    #     # --- STAGE 2: Cross-Encoder Reranking ---
    #     # Format candidates into the structure expected by FlashRank
    #     passages = [
    #         {
    #             "id": i,
    #             "text": chunk.text,
    #             "meta": {"chunk_obj": chunk} # Keep a reference to the original Chunk object
    #         }
    #         for i, chunk in enumerate(matched_chunks)
    #     ]
        
    #     # Execute the deep semantic scoring pass
    #     rerank_request = RerankRequest(query=query_text, passages=passages)
    #     rerank_results = reranker_model.rerank(rerank_request)
        
    #     # Reconstruct the sorted chunk list based on the new semantic scores
    #     final_ordered_chunks = [result["meta"]["chunk_obj"] for result in rerank_results]
        
    #     # Return the new optimized list (The new element at index 0 is your optimized Recall@1)
    #     return final_ordered_chunks
