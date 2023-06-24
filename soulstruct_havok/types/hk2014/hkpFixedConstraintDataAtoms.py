from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkpSetLocalTransformsConstraintAtom import hkpSetLocalTransformsConstraintAtom
from .hkpSetupStabilizationAtom import hkpSetupStabilizationAtom
from .hkpBallSocketConstraintAtom import hkpBallSocketConstraintAtom
from .hkp3dAngConstraintAtom import hkp3dAngConstraintAtom


@dataclass(slots=True, eq=False, repr=False)
class hkpFixedConstraintDataAtoms(hk):
    alignment = 16
    byte_size = 192
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "transforms", hkpSetLocalTransformsConstraintAtom),
        Member(144, "setupStabilization", hkpSetupStabilizationAtom),
        Member(160, "ballSocket", hkpBallSocketConstraintAtom),
        Member(176, "ang", hkp3dAngConstraintAtom),
    )
    members = local_members

    transforms: hkpSetLocalTransformsConstraintAtom
    setupStabilization: hkpSetupStabilizationAtom
    ballSocket: hkpBallSocketConstraintAtom
    ang: hkp3dAngConstraintAtom
