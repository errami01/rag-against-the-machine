from pathlib import Path
from typing import Any
from student.utils.project_root import get_project_root
import orjson


def save_json(path: str | Path, data: Any) -> None:
    path = Path(get_project_root() / path)

    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "wb") as f:
        f.write(
            orjson.dumps(
                data,
                option=orjson.OPT_INDENT_2,
            )
        )


def load_json(path: str | Path) -> Any:
    path = Path(get_project_root() / path)
    with open(path, "rb") as f:
        return orjson.loads(f.read())
