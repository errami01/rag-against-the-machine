from student.evaluation.overlap import is_match
from student.models.dataset import MinimalSource


def recall_at_k(
    retrieved: list[MinimalSource],
    gold: list[MinimalSource],
) -> float:

    if not gold:
        return 0.0

    found = 0

    for g in gold:
        if any(is_match(r, g) for r in retrieved):
            found += 1

    return found / len(gold)