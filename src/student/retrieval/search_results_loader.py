from pathlib import Path

from student.models.dataset import StudentSearchResults
from student.utils.json import load_json


def load_search_results(path: str | Path) -> StudentSearchResults:
    """Loads and validates saved search results from a JSON file.

    Reads raw data from the specified path and uses Pydantic validation to
    parse it into a structured data model.

    Args:
        path: The filesystem path (as a string or Path object) to
        the JSON file.

    Returns:
        A validated instance containing the search results configuration.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValidationError: If the JSON structure does not match the
          expected schema.
    """
    data = load_json(path)

    return StudentSearchResults.model_validate(data)
