from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkpConstraintData import hkpConstraintData


@dataclass(slots=True, eq=False, repr=False)
class hkpFixedConstraintData(hkpConstraintData):
    alignment = 16
    byte_size = 224
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 808115269

    local_members = (
        Member(32, "atoms", hkUlong),
    )
    members = hkpConstraintData.members + local_members

    atoms: int
