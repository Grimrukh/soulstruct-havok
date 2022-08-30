from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


from .hkpConstraintAtom import hkpConstraintAtom


class hkp2dAngConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(2, "freeRotationAxis", hkUint8),
    )
    members = hkpConstraintAtom.members + local_members

    freeRotationAxis: int
