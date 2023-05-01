from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


from .hkpConstraintData import hkpConstraintData


class hkpWrappedConstraintData(hkpConstraintData):
    alignment = 8
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member(24, "constraintData", hkRefPtr(hkpConstraintData, hsh=1491997840), MemberFlags.Protected),
    )
    members = hkpConstraintData.members + local_members

    constraintData: hkpConstraintData