from pathlib import Path
from student.utils.project_root import get_project_root

SUPPORTED_EXTENSIONS = {
    ".py",
    ".md",
    ".rst",
    ".txt",
}


def discover_files(root: Path) -> list[Path]:
    """
    Recursively discover supported files.
    """
    files: list[Path] = []
    root = get_project_root() / root
    for path in root.rglob("*"):
        if (
            path.is_file()
            and path.suffix.lower() in SUPPORTED_EXTENSIONS
        ):
            files.append(path)
    if not files:
        raise Exception("No file found")
    return files
