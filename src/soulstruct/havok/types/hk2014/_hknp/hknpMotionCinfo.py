from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpMotionCinfo(hk):
    alignment = 16
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(0, "motionPropertiesId", hkUint16),
        Member(2, "enableDeactivation", hkBool),
        Member(4, "inverseMass", hkReal),
        Member(8, "massFactor", hkReal),
        Member(12, "maxLinearAccelerationDistancePerStep", hkReal),
        Member(16, "maxRotationToPreventTunneling", hkReal),
        Member(32, "inverseInertiaLocal", hkVector4),
        Member(48, "centerOfMassWorld", hkVector4),
        Member(64, "orientation", hkQuaternionf),
        Member(80, "linearVelocity", hkVector4),
        Member(96, "angularVelocity", hkVector4),
    )
    members = local_members

    motionPropertiesId: int
    enableDeactivation: bool
    inverseMass: float
    massFactor: float
    maxLinearAccelerationDistancePerStep: float
    maxRotationToPreventTunneling: float
    inverseInertiaLocal: Vector4
    centerOfMassWorld: Vector4
    orientation: hkQuaternionf
    linearVelocity: Vector4
    angularVelocity: Vector4
