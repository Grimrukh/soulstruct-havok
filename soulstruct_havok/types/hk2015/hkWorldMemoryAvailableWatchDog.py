from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hkWorldMemoryAvailableWatchDog(hkReferencedObject):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 61
    __abstract_value = 3
    __version = 1
    local_members = ()
