from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkpSetLocalTransformsConstraintAtom import hkpSetLocalTransformsConstraintAtom
from .hkpSetupStabilizationAtom import hkpSetupStabilizationAtom
from .hkpRagdollMotorConstraintAtom import hkpRagdollMotorConstraintAtom
from .hkpAngFrictionConstraintAtom import hkpAngFrictionConstraintAtom
from .hkpTwistLimitConstraintAtom import hkpTwistLimitConstraintAtom
from .hkpConeLimitConstraintAtom import hkpConeLimitConstraintAtom
from .hkpBallSocketConstraintAtom import hkpBallSocketConstraintAtom


@dataclass(slots=True, eq=False, repr=False)
class hkpRagdollConstraintDataAtoms(hk):
    alignment = 16
    byte_size = 384
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1
    __real_name = "hkpRagdollConstraintData::Atoms"

    local_members = (
        Member(0, "transforms", hkpSetLocalTransformsConstraintAtom),
        Member(144, "setupStabilization", hkpSetupStabilizationAtom),
        Member(160, "ragdollMotors", hkpRagdollMotorConstraintAtom),
        Member(256, "angFriction", hkpAngFrictionConstraintAtom),
        Member(272, "twistLimit", hkpTwistLimitConstraintAtom),
        Member(304, "coneLimit", hkpConeLimitConstraintAtom),
        Member(336, "planesLimit", hkpConeLimitConstraintAtom),
        Member(368, "ballSocket", hkpBallSocketConstraintAtom),
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
