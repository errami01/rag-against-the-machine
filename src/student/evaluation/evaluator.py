from student.utils.json import load_json
from student.datasets.loader import load_dataset

from student.models.dataset import StudentSearchResults
from student.evaluation.recall import recall_at_k


class Evaluator:
    """An evaluation engine for calculating RAG retrieval quality metrics.

    This engine parses student search submissions, aligns them against a
    ground-truth dataset, and computes statistical accuracy measurements.
    """

    def evaluate(
        self,
        student_path: str,
        dataset_path: str,
        k: int = 10,
    ) -> None:
        """Evaluate student search footprints against the reference dataset.

        Loads the student and ground-truth manifests, extracts question-level
        source intersections, and computes the average Recall@K metrics at
        predefined cutoff windows before displaying results to the console.

        Args:
            student_path: The file path to the student search results JSON.
            dataset_path: The file path to the gold-standard dataset JSON.
            k: The absolute maximum retrieval evaluation depth limit.
              Defaults to 10.

        Raises:
            OSError: If reading either file path from disk fails.
            ValidationError: If JSON contents do not comply with the
              expected target Pydantic schemas.
        """
        dataset = load_dataset(dataset_path)

        student = StudentSearchResults.model_validate(
            load_json(student_path)
        )

        lookup = {
            r.question_id: r
            for r in student.search_results
        }

        r1, r3, r5, r10 = [], [], [], []
        for q in dataset.rag_questions:
            if not getattr(q, "sources", None):
                continue

            res = lookup.get(q.question_id)
            if not res:
                continue

            r1.append(
                recall_at_k(
                    res.retrieved_sources[:1],
                    q.sources,
                )
            )

            r3.append(
                recall_at_k(
                    res.retrieved_sources[:3],
                    q.sources,
                )
            )

            r5.append(
                recall_at_k(
                    res.retrieved_sources[:5],
                    q.sources,
                )
            )

            r10.append(
                recall_at_k(
                    res.retrieved_sources[:10],
                    q.sources,
                )
            )

        def avg(x):
            return sum(x) / len(x) if x else 0.0

        print("\n🎯 Evaluation Results")
        print("=" * 40)
        print(f"Questions evaluated: {len(r5)}")
        print(f"Recall@1: {avg(r1):.3f}")
        print(f"Recall@3: {avg(r3):.3f}")
        print(f"Recall@5: {avg(r5):.3f}")
        print(f"Recall@10: {avg(r10):.3f}")
