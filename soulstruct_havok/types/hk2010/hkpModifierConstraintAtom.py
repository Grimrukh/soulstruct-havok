from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkpConstraintAtom import hkpConstraintAtom


@dataclass(slots=True, eq=False, repr=False)
class hkpModifierConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "modifierAtomSize", hkUint16),
        Member(18, "childSize", hkUint16),
        Member(20, "child", Ptr(hkpConstraintAtom)),
        Member(24, "pad", hkStruct(hkUint32, 2)),
    )
    members = hkpConstraintAtom.members + local_members

    modifierAtomSize: int
    childSize: int
    child: hkpConstraintAtom
    pad: tuple[int, ...]
