from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkpConstraintData import hkpConstraintData
from .hkpRagdollConstraintDataAtoms import hkpRagdollConstraintDataAtoms


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpRagdollConstraintData(hkpConstraintData):
    alignment = 16
    byte_size = 352
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2411060521

    local_members = (
        Member(16, "atoms", hkpRagdollConstraintDataAtoms),
    )
    members = hkpConstraintData.members + local_members

    atoms: hkpRagdollConstraintDataAtoms
