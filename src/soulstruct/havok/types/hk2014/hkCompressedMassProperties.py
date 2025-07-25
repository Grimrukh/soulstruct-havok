from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkCompressedMassProperties(hk):
    alignment = 16
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "centerOfMass", hkStruct(hkInt16, 4)),
        Member(8, "inertia", hkStruct(hkInt16, 4)),
        Member(16, "majorAxisSpace", hkStruct(hkInt16, 4)),
        Member(24, "mass", hkReal),
        Member(28, "volume", hkReal),
    )
    members = local_members

    centerOfMass: tuple[int, ...]
    inertia: tuple[int, ...]
    majorAxisSpace: tuple[int, ...]
    mass: float
    volume: float
