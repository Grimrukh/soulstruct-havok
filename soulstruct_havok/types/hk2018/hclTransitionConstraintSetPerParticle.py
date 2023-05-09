from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hclTransitionConstraintSetPerParticle(hk):
    alignment = 4
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 1322749721
    __version = 1
    __real_name = "hclTransitionConstraintSet::PerParticle"

    local_members = (
        Member(0, "particleIndex", hkUint16),
        Member(2, "referenceVertex", hkUint16),
        Member(4, "toAnimDelay", hkReal),
        Member(8, "toSimDelay", hkReal),
        Member(12, "toSimMaxDistance", hkReal),
    )
    members = local_members

    particleIndex: int
    referenceVertex: int
    toAnimDelay: float
    toSimDelay: float
    toSimMaxDistance: float
