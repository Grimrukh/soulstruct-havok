from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaiIndex(hkInt32):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()
