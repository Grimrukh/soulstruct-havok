from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *



from .hknpMotionPropertiesDeactivationSettings import hknpMotionPropertiesDeactivationSettings
from .hknpMotionPropertiesFullCastSettings import hknpMotionPropertiesFullCastSettings


@dataclass(slots=True, eq=False, repr=False)
class hknpMotionProperties(hk):
    alignment = 16
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 2032698156
    __version = 5

    local_members = (
        Member(0, "isExclusive", hkUint32),
        Member(4, "flags", _unsigned_int),
        Member(8, "gravityFactor", hkReal),
        Member(12, "timeFactor", hkReal),
        Member(16, "maxLinearSpeed", hkReal),
        Member(20, "maxAngularSpeed", hkReal),
        Member(24, "linearDamping", hkReal),
        Member(28, "angularDamping", hkReal),
        Member(32, "solverStabilizationSpeedThreshold", hkReal),
        Member(36, "solverStabilizationSpeedReduction", hkReal),
        Member(40, "deactivationSettings", hknpMotionPropertiesDeactivationSettings),
        Member(64, "fullCastSettings", hknpMotionPropertiesFullCastSettings),
    )
    members = local_members

    isExclusive: int
    flags: int
    gravityFactor: float
    timeFactor: float
    maxLinearSpeed: float
    maxAngularSpeed: float
    linearDamping: float
    angularDamping: float
    solverStabilizationSpeedThreshold: float
    solverStabilizationSpeedReduction: float
    deactivationSettings: hknpMotionPropertiesDeactivationSettings
    fullCastSettings: hknpMotionPropertiesFullCastSettings
