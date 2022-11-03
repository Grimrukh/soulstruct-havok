__all__ = ["PACKAGE_PATH"]

import sys
from pathlib import Path


def PACKAGE_PATH(*relative_parts) -> Path:
    """Returns resolved path of given files in `soulstruct-havok` package directory (the actual namespace directory
    containing `__init__`, NOT the one above it containing `setup.py`)."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS"), *relative_parts)
    return Path(__file__).parent.parent.resolve().joinpath(*relative_parts)
