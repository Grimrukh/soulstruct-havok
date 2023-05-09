from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkp2dAngConstraintAtom import hkp2dAngConstraintAtom
from .hkpAngFrictionConstraintAtom import hkpAngFrictionConstraintAtom
from .hkpAngLimitConstraintAtom import hkpAngLimitConstraintAtom
from .hkpAngMotorConstraintAtom import hkpAngMotorConstraintAtom
from .hkpBallSocketConstraintAtom import hkpBallSocketConstraintAtom
from .hkpSetLocalTransformsConstraintAtom import hkpSetLocalTransformsConstraintAtom
from .hkpSetupStabilizationAtom import hkpSetupStabilizationAtom


@dataclass(slots=True, eq=False, repr=False)
class hkpLimitedHingeConstraintDataAtoms(hk):
    alignment = 16
    byte_size = 272
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(0, "transforms", hkpSetLocalTransformsConstraintAtom),
        Member(144, "setupStabilization", hkpSetupStabilizationAtom),
        Member(160, "angMotor", hkpAngMotorConstraintAtom),
        Member(200, "angFriction", hkpAngFrictionConstraintAtom),
        Member(216, "angLimit", hkpAngLimitConstraintAtom),
        Member(232, "2dAng", hkp2dAngConstraintAtom),
        Member(248, "ballSocket", hkpBallSocketConstraintAtom),
    )
    members = local_members

    transforms: hkpSetLocalTransformsConstraintAtom
    setupStabilization: hkpSetupStabilizationAtom
    angMotor: hkpAngMotorConstraintAtom
    angFriction: hkpAngFrictionConstraintAtom
    angLimit: hkpAngLimitConstraintAtom
    ballSocket: hkpBallSocketConstraintAtom
