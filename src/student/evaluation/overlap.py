from student.models.dataset import MinimalSource


def overlap_ratio(a: MinimalSource, b: MinimalSource) -> float:
    """Calculate the ratio of source B that is covered by source A.

    Computes the character-level intersection between two document sources
    and normalizes the overlapping length by the total length of the
      gold-truth source B.

    Args:
        a: The retrieved candidate source snippet to inspect.
        b: The ground-truth reference source snippet (denominator context).

    Returns:
        The percentage of source B overlapped by source A as a floating-point
        value between 0.0 and 1.0. Returns 0.0 if file paths do not match
          or if source B has a non-positive length.
    """
    if a.file_path != b.file_path:
        return 0.0

    start = max(a.first_character_index, b.first_character_index)
    end = min(a.last_character_index, b.last_character_index)

    overlap = max(0, end - start)

    denom = b.last_character_index - b.first_character_index
    if denom <= 0:
        return 0.0

    return overlap / denom


def is_match(retrieved: MinimalSource, gold: MinimalSource) -> bool:
    """Determine if a retrieved source sufficiently matches a ground-truth
      chunk.

    Evaluates if the character overlap ratio covers at least a strict 5 percent
    threshold of the target gold-truth content.

    Args:
        retrieved: The source snippet extracted by the search engine index.
        gold: The ground-truth source reference chunk.

    Returns:
        True if the overlap ratio is greater than or equal to 0.05,
        otherwise False.
    """
    return overlap_ratio(retrieved, gold) >= 0.05
