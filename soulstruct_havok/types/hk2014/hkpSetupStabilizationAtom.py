from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hkpConstraintAtom import hkpConstraintAtom


class hkpSetupStabilizationAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 3

    local_members = (
        Member(2, "enabled", hkBool),
        Member(3, "padding", hkStruct(hkUint8, 1), MemberFlags.NotSerializable),
        Member(4, "maxLinImpulse", hkReal),
        Member(8, "maxAngImpulse", hkReal),
        Member(12, "maxAngle", hkReal),
    )
    members = hkpConstraintAtom.members + local_members

    enabled: bool
    padding: tuple[int, ...]
    maxLinImpulse: float
    maxAngImpulse: float
    maxAngle: float
