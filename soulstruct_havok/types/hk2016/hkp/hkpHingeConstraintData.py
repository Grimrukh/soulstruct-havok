from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkpConstraintData import hkpConstraintData
from .hkpHingeConstraintDataAtoms import hkpHingeConstraintDataAtoms


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpHingeConstraintData(hkpConstraintData):
    alignment = 16
    byte_size = 224
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1381497954

    local_members = (
        Member(32, "atoms", hkpHingeConstraintDataAtoms),
    )
    members = hkpConstraintData.members + local_members

    atoms: hkpHingeConstraintDataAtoms
