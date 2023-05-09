from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hknpLodManagerCinfo(hk):
    alignment = 4
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(0, "registerDefaultConfig", hkBool),
        Member(1, "autoBuildLodOnDynamicBodyAdded", hkBool),
        Member(2, "autoBuildLodOnMeshBodyAdded", hkBool),
        Member(4, "lodAccuray", hkReal),
        Member(8, "slowToFastThreshold", hkReal),
        Member(12, "fastToSlowThreshold", hkReal),
        Member(16, "bodyIsBigThreshold", hkReal),
        Member(20, "avgVelocityGain", hkReal),
    )
    members = local_members

    registerDefaultConfig: bool
    autoBuildLodOnDynamicBodyAdded: bool
    autoBuildLodOnMeshBodyAdded: bool
    lodAccuray: float
    slowToFastThreshold: float
    fastToSlowThreshold: float
    bodyIsBigThreshold: float
    avgVelocityGain: float
