from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpMotionProperties(hk):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 3

    local_members = (
        Member(0, "isExclusive", hkUint32),
        Member(4, "flags", hkFlags(hkUint32)),
        Member(8, "gravityFactor", hkReal),
        Member(12, "timeFactor", hkReal),
        Member(16, "maxLinearSpeed", hkReal),
        Member(20, "maxAngularSpeed", hkReal),
        Member(24, "linearDamping", hkReal),
        Member(28, "angularDamping", hkReal),
        Member(32, "solverStabilizationSpeedThreshold", hkReal),
        Member(36, "solverStabilizationSpeedReduction", hkReal),
        Member(40, "maxDistSqrd", hkReal),
        Member(44, "maxRotSqrd", hkReal),
        Member(48, "invBlockSize", hkReal),
        Member(52, "pathingUpperThreshold", hkInt16),
        Member(54, "pathingLowerThreshold", hkInt16),
        Member(56, "numDeactivationFrequencyPasses", hkUint8),
        Member(57, "deactivationVelocityScaleSquare", hkUint8),
        Member(58, "minimumPathingVelocityScaleSquare", hkUint8),
        Member(59, "spikingVelocityScaleThresholdSquared", hkUint8),
        Member(60, "minimumSpikingVelocityScaleSquared", hkUint8),
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
