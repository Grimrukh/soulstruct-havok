from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hkaBone(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(8, "lockTranslation", hkBool),
    )
    members = local_members

    name: str
    lockTranslation: bool
