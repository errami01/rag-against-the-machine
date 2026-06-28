from student.models.dataset import MinimalSource


def overlap_ratio(a: MinimalSource, b: MinimalSource) -> float:
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
    return overlap_ratio(retrieved, gold) >= 0.05