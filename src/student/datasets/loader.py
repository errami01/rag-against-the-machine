from pathlib import Path

from student.models.dataset import RagDataset
from student.utils.json import load_json


def load_dataset(path: str | Path) -> RagDataset:
    """Loads and validates an evaluation dataset from a JSON file.

    Reads raw data from the specified path and handles parsing through the
    RagDataset Pydantic model to enforce strict schema adherence for
    evaluation questions.

    Args:
        path: The filesystem path (as a string or Path object) to the JSON
        dataset file.

    Returns:
        An instantiated and schema-validated RagDataset instance.

    Raises:
        FileNotFoundError: If the specified file does not exist on disk.
        ValidationError: If the JSON file contains structures that do not
        comply with the RagDataset data schema requirements.
    """
    data = load_json(path)
    return RagDataset.model_validate(data)
