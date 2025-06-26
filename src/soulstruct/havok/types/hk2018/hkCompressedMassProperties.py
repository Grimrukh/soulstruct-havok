from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from .core import *
from .hkPackedVector3 import hkPackedVector3


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkCompressedMassProperties(hk):
    alignment = 12296
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(0, "centerOfMass", hkPackedVector3),
        Member(8, "inertia", hkPackedVector3),
        Member(16, "majorAxisSpace", hkGenericStruct(_short, 4)),
        Member(24, "mass", hkReal),
        Member(28, "volume", hkReal),
    )
    members = local_members

    centerOfMass: hkPackedVector3
    inertia: hkPackedVector3
    majorAxisSpace: tuple[_short]
    mass: float
    volume: float
