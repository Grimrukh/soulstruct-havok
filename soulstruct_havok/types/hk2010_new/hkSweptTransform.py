from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


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

    centerOfMass0: hkVector4
    centerOfMass1: hkVector4
    rotation0: hkQuaternionf
    rotation1: hkQuaternionf
    centerOfMassLocal: hkVector4
