from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *




class hknpMassDistribution(hk):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "centerOfMassAndVolume", hkVector4),
        Member(16, "majorAxisSpace", hkQuaternion),
        Member(32, "inertiaTensor", hkVector4),
    )
    members = local_members

    centerOfMassAndVolume: Vector4
    majorAxisSpace: hkQuaternion
    inertiaTensor: Vector4