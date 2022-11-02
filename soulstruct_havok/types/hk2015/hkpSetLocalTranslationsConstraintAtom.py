from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


from .hkpConstraintAtom import hkpConstraintAtom


class hkpSetLocalTranslationsConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "translationA", hkVector4),
        Member(32, "translationB", hkVector4),
    )
    members = hkpConstraintAtom.members + local_members

    translationA: Vector4
    translationB: Vector4
