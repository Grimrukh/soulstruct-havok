from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkpAngFrictionConstraintAtom import hkpAngFrictionConstraintAtom
from .hkpBallSocketConstraintAtom import hkpBallSocketConstraintAtom
from .hkpConeLimitConstraintAtom import hkpConeLimitConstraintAtom
from .hkpRagdollMotorConstraintAtom import hkpRagdollMotorConstraintAtom
from .hkpSetLocalTransformsConstraintAtom import hkpSetLocalTransformsConstraintAtom
from .hkpSetupStabilizationAtom import hkpSetupStabilizationAtom
from .hkpTwistLimitConstraintAtom import hkpTwistLimitConstraintAtom


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpRagdollConstraintDataAtoms(hk):
    alignment = 16
    byte_size = 384
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

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
