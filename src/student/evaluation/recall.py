from student.evaluation.overlap import is_match
from student.models.dataset import MinimalSource


def recall_at_k(
    retrieved: list[MinimalSource],
    gold: list[MinimalSource],
) -> float:
    """Calculate the recall metric for a set of retrieved source snippets.

    Measures the proportion of ground-truth sources that are successfully
    recalled by any candidate source present in the retrieved window list,
    leveraging the threshold-based matching utility.

    Args:
        retrieved: A slice list of top-K candidate sources isolated by the
          search engine.
        gold: The complete list of ground-truth source references.

    Returns:
        The fraction of gold-truth sources successfully recovered as a
        floating-point value between 0.0 and 1.0. Returns 0.0 if the gold
        reference collection is empty.
    """
    if not gold:
        return 0.0

    found = 0

    for g in gold:
        if any(is_match(r, g) for r in retrieved):
            found += 1

    return found / len(gold)
