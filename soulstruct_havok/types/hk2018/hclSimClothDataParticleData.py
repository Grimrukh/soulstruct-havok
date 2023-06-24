from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hclSimClothDataParticleData(hk):
    alignment = 4
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 2467200052
    __version = 2
    __real_name = "hclSimClothData::ParticleData"

    local_members = (
        Member(0, "mass", hkReal),
        Member(4, "invMass", hkReal),
        Member(8, "radius", hkReal),
        Member(12, "friction", hkReal),
    )
    members = local_members

    mass: float
    invMass: float
    radius: float
    friction: float
