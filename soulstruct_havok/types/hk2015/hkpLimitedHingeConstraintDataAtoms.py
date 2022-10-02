from __future__ import annotations

from soulstruct_havok.enums import *
from soulstruct_havok.types.core import *
from .hkp2dAngConstraintAtom import hkp2dAngConstraintAtom
from .hkpAngFrictionConstraintAtom import hkpAngFrictionConstraintAtom
from .hkpAngLimitConstraintAtom import hkpAngLimitConstraintAtom
from .hkpAngMotorConstraintAtom import hkpAngMotorConstraintAtom
from .hkpBallSocketConstraintAtom import hkpBallSocketConstraintAtom
from .hkpSetLocalTransformsConstraintAtom import hkpSetLocalTransformsConstraintAtom
from .hkpSetupStabilizationAtom import hkpSetupStabilizationAtom


class hkpLimitedHingeConstraintDataAtoms(hk):
    alignment = 16
    byte_size = 272
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1
    __real_name = "hkpLimitedHingeConstraintData::Atoms"

    local_members = (
        Member(0, "transforms", hkpSetLocalTransformsConstraintAtom),
        Member(144, "setupStabilization", hkpSetupStabilizationAtom),
        Member(160, "angMotor", hkpAngMotorConstraintAtom),
        Member(192, "angFriction", hkpAngFrictionConstraintAtom),
        Member(208, "angLimit", hkpAngLimitConstraintAtom),
        Member(240, "2dAng", hkp2dAngConstraintAtom),
        Member(256, "ballSocket", hkpBallSocketConstraintAtom),
    )
    members = local_members

    transforms: hkpSetLocalTransformsConstraintAtom
    setupStabilization: hkpSetupStabilizationAtom
    angMotor: hkpAngMotorConstraintAtom
    angFriction: hkpAngFrictionConstraintAtom
    angLimit: hkpAngLimitConstraintAtom
    ballSocket: hkpBallSocketConstraintAtom
