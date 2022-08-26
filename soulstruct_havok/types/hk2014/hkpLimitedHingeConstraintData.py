from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hkpConstraintData import hkpConstraintData
from .hkpLimitedHingeConstraintDataAtoms import hkpLimitedHingeConstraintDataAtoms


class hkpLimitedHingeConstraintData(hkpConstraintData):
    alignment = 16
    byte_size = 304
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1374314554

    local_members = (
        Member(32, "atoms", hkpLimitedHingeConstraintDataAtoms),
    )
    members = hkpConstraintData.members + local_members

    atoms: hkpLimitedHingeConstraintDataAtoms
