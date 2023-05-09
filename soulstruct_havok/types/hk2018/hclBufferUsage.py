from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hclBufferUsage(hk):
    alignment = 1
    byte_size = 5
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "perComponentFlags", hkGenericStruct(hkUint8, 4)),
        Member(4, "trianglesRead", hkBool),
    )
    members = local_members

    perComponentFlags: tuple[hkUint8]
    trianglesRead: bool
