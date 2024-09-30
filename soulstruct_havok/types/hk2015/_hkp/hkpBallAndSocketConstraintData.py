from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *

from .hkpConstraintData import hkpConstraintData
from .hkpBallAndSocketConstraintDataAtoms import hkpBallAndSocketConstraintDataAtoms


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpBallAndSocketConstraintData(hkpConstraintData):
    alignment = 16
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3392701812

    local_members = (
        Member(32, "atoms", hkpBallAndSocketConstraintDataAtoms),
    )
    members = hkpConstraintData.members + local_members

    atoms: hkpBallAndSocketConstraintDataAtoms
