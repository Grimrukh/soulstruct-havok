from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaiPackedKey_(_unsigned_int):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()
