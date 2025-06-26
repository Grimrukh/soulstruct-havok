from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkpConstraintData import hkpConstraintData
from .hkpRagdollConstraintDataAtoms import hkpRagdollConstraintDataAtoms


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpRagdollConstraintData(hkpConstraintData):
    alignment = 16
    byte_size = 416
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3078430774

    local_members = (
        Member(32, "atoms", hkpRagdollConstraintDataAtoms),
    )
    members = hkpConstraintData.members + local_members

    atoms: hkpRagdollConstraintDataAtoms
