from __future__ import annotations

__all__ = ["SOULSTRUCT_HAVOK_PATH"]

from pathlib import Path


def SOULSTRUCT_HAVOK_PATH(*relative_parts) -> Path:
    """Returns resolved path of given files in `soulstruct-havok` package directory (`'soulstruct'`).

    Parts should essentially always start with `'havok'`.
    """

    parent = Path(__file__).parent
    while parent.name != "soulstruct":
        parent = parent.parent

    if not relative_parts:
        return parent.resolve()  # 'soulstruct' namespace directory

    return Path(parent, *relative_parts).resolve()