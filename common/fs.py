from pathlib import Path
from typing import Generator


def get_all_files(root: str, extension: str = "*.md") -> Generator:
    """
    Get all files recursively with a given extension
    @rtype: object
    """
    return Path(root).rglob(extension)
