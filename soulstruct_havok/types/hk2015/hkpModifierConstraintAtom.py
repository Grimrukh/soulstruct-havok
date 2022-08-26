from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hkpConstraintAtom import hkpConstraintAtom


class hkpModifierConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(16, "modifierAtomSize", hkUint16),
        Member(18, "childSize", hkUint16),
        Member(24, "child", Ptr(hkpConstraintAtom)),
        Member(32, "pad", hkGenericStruct(hkUint32, 2), MemberFlags.NotSerializable),
    )
    members = hkpConstraintAtom.members + local_members

    modifierAtomSize: int
    childSize: int
    child: hkpConstraintAtom
    pad: tuple[hkUint32]
