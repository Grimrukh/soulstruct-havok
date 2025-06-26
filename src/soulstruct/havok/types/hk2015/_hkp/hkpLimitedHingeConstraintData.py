from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkpConstraintData import hkpConstraintData
from .hkpLimitedHingeConstraintDataAtoms import hkpLimitedHingeConstraintDataAtoms


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpLimitedHingeConstraintData(hkpConstraintData):
    alignment = 16
    byte_size = 304
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3074916163

    local_members = (
        Member(32, "atoms", hkpLimitedHingeConstraintDataAtoms),
    )
    members = hkpConstraintData.members + local_members

    atoms: hkpLimitedHingeConstraintDataAtoms
