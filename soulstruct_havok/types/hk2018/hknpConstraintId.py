from __future__ import annotations

from .core import *
from .hkHandle import hkHandle


@dataclass(slots=True, eq=False, repr=False)
class hknpConstraintId(hkHandle):
    """Havok alias."""
    __tag_format_flags = 4
    __version = 1
    local_members = ()
