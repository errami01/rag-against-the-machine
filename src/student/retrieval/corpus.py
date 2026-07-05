
from student.models import Chunk
from student.utils.json import save_json


def save_chunks(chunks: list[Chunk], output_path: str) -> None:
    """Serializes a list of Chunk objects and saves them as a JSON file.

    Args:
        chunks: A list of Chunk objects to be serialized.
        output_path: The file path where the JSON data will be saved.

    Returns:
        None.
    """
    save_json(
        output_path,
        [
            chunk.model_dump()
            for chunk in chunks
        ],
    )
