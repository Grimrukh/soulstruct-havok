from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkpConstraintData import hkpConstraintData
from .hkpRagdollConstraintDataAtoms import hkpRagdollConstraintDataAtoms


@dataclass(slots=True, eq=False, repr=False)
class hkpRagdollConstraintData(hkpConstraintData):
    alignment = 16
    byte_size = 416
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3431273257

    local_members = (
        Member(32, "atoms", hkpRagdollConstraintDataAtoms),
    )
    members = hkpConstraintData.members + local_members

    atoms: hkpRagdollConstraintDataAtoms
