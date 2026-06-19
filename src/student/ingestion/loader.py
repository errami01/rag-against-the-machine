from pathlib import Path


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

    for path in root.rglob("*"):
        if (
            path.is_file()
            and path.suffix.lower() in SUPPORTED_EXTENSIONS
        ):
            files.append(path)

    return files