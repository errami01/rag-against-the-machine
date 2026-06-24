from pathlib import Path

from student.models.dataset import RagDataset
from student.utils.json import load_json


def load_dataset(path: str | Path) -> RagDataset:
    data = load_json(path)
    return RagDataset.model_validate(data)