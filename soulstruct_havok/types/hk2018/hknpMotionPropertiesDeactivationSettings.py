from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hknpMotionPropertiesDeactivationSettings(hk):
    alignment = 4
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hknpMotionProperties::DeactivationSettings"

    local_members = (
        Member(0, "maxDistSqrd", hkReal),
        Member(4, "maxRotSqrd", hkReal),
        Member(8, "invBlockSize", hkReal),
        Member(12, "pathingUpperThreshold", hkInt16),
        Member(14, "pathingLowerThreshold", hkInt16),
        Member(16, "numDeactivationFrequencyPasses", hkUint8),
        Member(17, "deactivationVelocityScaleSquare", hkUint8),
        Member(18, "minimumPathingVelocityScaleSquare", hkUint8),
        Member(19, "spikingVelocityScaleThresholdSquared", hkUint8),
        Member(20, "minimumSpikingVelocityScaleSquared", hkUint8),
    )
    members = local_members

    maxDistSqrd: float
    maxRotSqrd: float
    invBlockSize: float
    pathingUpperThreshold: int
    pathingLowerThreshold: int
    numDeactivationFrequencyPasses: int
    deactivationVelocityScaleSquare: int
    minimumPathingVelocityScaleSquare: int
    spikingVelocityScaleThresholdSquared: int
    minimumSpikingVelocityScaleSquared: int
