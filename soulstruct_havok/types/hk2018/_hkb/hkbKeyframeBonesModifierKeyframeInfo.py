from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbKeyframeBonesModifierKeyframeInfo(hk):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1695728796
    __real_name = "hkbKeyframeBonesModifier::KeyframeInfo"

    local_members = (
        Member(0, "keyframedPosition", hkVector4),
        Member(16, "keyframedRotation", hkQuaternion),
        Member(32, "boneIndex", hkInt16),
        Member(34, "isValid", hkBool),
    )
    members = local_members

    keyframedPosition: hkVector4
    keyframedRotation: hkQuaternion
    boneIndex: int
    isValid: bool
