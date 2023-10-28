from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hclConstraintSet import hclConstraintSet
from .hclTransitionConstraintSetPerParticle import hclTransitionConstraintSetPerParticle


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclTransitionConstraintSet(hclConstraintSet):
    alignment = 8
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 42297855
    __version = 1

    local_members = (
        Member(40, "perParticleData", hkArray(hclTransitionConstraintSetPerParticle, hsh=2562328436)),
        Member(56, "toAnimPeriod", hkReal),
        Member(60, "toAnimPlusDelayPeriod", hkReal),
        Member(64, "toSimPeriod", hkReal),
        Member(68, "toSimPlusDelayPeriod", hkReal),
        Member(72, "referenceMeshBufferIdx", hkUint32),
    )
    members = hclConstraintSet.members + local_members

    perParticleData: list[hclTransitionConstraintSetPerParticle]
    toAnimPeriod: float
    toAnimPlusDelayPeriod: float
    toSimPeriod: float
    toSimPlusDelayPeriod: float
    referenceMeshBufferIdx: int
