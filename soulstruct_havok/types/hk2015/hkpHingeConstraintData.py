from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


from .hkpConstraintData import hkpConstraintData
from .hkpHingeConstraintDataAtoms import hkpHingeConstraintDataAtoms


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