from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
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
