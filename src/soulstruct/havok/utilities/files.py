from __future__ import annotations

__all__ = ["HAVOK_PACKAGE_PATH"]

import sys
from pathlib import Path


def HAVOK_PACKAGE_PATH(*relative_parts) -> Path:
    """Returns resolved path of given files in `soulstruct/havok` package directory."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS"), *relative_parts)  # TODO: confirm this is still correct with 'src'
    return Path(__file__).parent.parent.resolve().joinpath(*relative_parts)
