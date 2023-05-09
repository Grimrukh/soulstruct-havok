from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkpAngFrictionConstraintAtom import hkpAngFrictionConstraintAtom
from .hkpBallSocketConstraintAtom import hkpBallSocketConstraintAtom
from .hkpConeLimitConstraintAtom import hkpConeLimitConstraintAtom
from .hkpRagdollMotorConstraintAtom import hkpRagdollMotorConstraintAtom
from .hkpSetLocalTransformsConstraintAtom import hkpSetLocalTransformsConstraintAtom
from .hkpSetupStabilizationAtom import hkpSetupStabilizationAtom
from .hkpTwistLimitConstraintAtom import hkpTwistLimitConstraintAtom


@dataclass(slots=True, eq=False, repr=False)
class hkpRagdollConstraintDataAtoms(hk):
    alignment = 16
    byte_size = 336
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "transforms", hkpSetLocalTransformsConstraintAtom),
        Member(144, "setupStabilization", hkpSetupStabilizationAtom),
        Member(160, "ragdollMotors", hkpRagdollMotorConstraintAtom),
        Member(240, "angFriction", hkpAngFrictionConstraintAtom),
        Member(252, "twistLimit", hkpTwistLimitConstraintAtom),
        Member(272, "coneLimit", hkpConeLimitConstraintAtom),
        Member(292, "planesLimit", hkpConeLimitConstraintAtom),
        Member(312, "ballSocket", hkpBallSocketConstraintAtom),
    )
    members = local_members

    transforms: hkpSetLocalTransformsConstraintAtom
    setupStabilization: hkpSetupStabilizationAtom
    ragdollMotors: hkpRagdollMotorConstraintAtom
    angFriction: hkpAngFrictionConstraintAtom
    twistLimit: hkpTwistLimitConstraintAtom
    coneLimit: hkpConeLimitConstraintAtom
    planesLimit: hkpConeLimitConstraintAtom
    ballSocket: hkpBallSocketConstraintAtom
