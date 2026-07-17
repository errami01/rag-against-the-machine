from pathlib import Path


def get_project_root() -> Path:
    """Traverses upward to find the root directory containing a marker
      file."""
    current = Path(__file__).resolve()
    
    # Keep going up until we find a root marker (like .git or pyproject.toml)
    for parent in current.parents:
        if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
            return parent
            
    # Fallback to the current file's parent if no marker is found
    return current.parent