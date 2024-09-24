from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkSweptTransform(hk):
    alignment = 16
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "centerOfMass0", hkVector4),
        Member(16, "centerOfMass1", hkVector4),
        Member(32, "rotation0", hkQuaternionf),
        Member(48, "rotation1", hkQuaternionf),
        Member(64, "centerOfMassLocal", hkVector4),
    )
    members = local_members

    centerOfMass0: Vector4
    centerOfMass1: Vector4
    rotation0: hkQuaternionf
    rotation1: hkQuaternionf
    centerOfMassLocal: Vector4
