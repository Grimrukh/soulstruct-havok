from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpSimpleMeshShapeTriangle(hk):
    alignment = 4
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    local_members = (
        Member(0, "a", hkInt32),
        Member(4, "b", hkInt32),
        Member(8, "c", hkInt32),
        Member(12, "weldingInfo", hkUint16),
    )

    a: int
    b: int
    c: int
    weldingInfo: int = 0
