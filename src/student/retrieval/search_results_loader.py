from pathlib import Path

from student.models.dataset import StudentSearchResults
from student.utils.json import load_json


def load_search_results(
    path: str | Path,
) -> StudentSearchResults:

    data = load_json(path)

    return StudentSearchResults.model_validate(data)