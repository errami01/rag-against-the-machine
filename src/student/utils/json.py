from pathlib import Path
from typing import Any

import orjson


def save_json(path: str | Path, data: Any) -> None:
    path = Path(path)

    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "wb") as f:
        f.write(
            orjson.dumps(
                data,
                option=orjson.OPT_INDENT_2,
            )
        )


def load_json(path: str | Path) -> Any:
    with open(path, "rb") as f:
        return orjson.loads(f.read())