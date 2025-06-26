from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *

from .hkpSetLocalTranslationsConstraintAtom import hkpSetLocalTranslationsConstraintAtom
from .hkpSetupStabilizationAtom import hkpSetupStabilizationAtom
from .hkpBallSocketConstraintAtom import hkpBallSocketConstraintAtom


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpBallAndSocketConstraintDataAtoms(hk):
    alignment = 16
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1
    __real_name = "hkpBallAndSocketConstraintData::Atoms"

    local_members = (
        Member(0, "pivots", hkpSetLocalTranslationsConstraintAtom),
        Member(48, "setupStabilization", hkpSetupStabilizationAtom),
        Member(64, "ballSocket", hkpBallSocketConstraintAtom),
    )
    members = local_members

    pivots: hkpSetLocalTranslationsConstraintAtom
    setupStabilization: hkpSetupStabilizationAtom
    ballSocket: hkpBallSocketConstraintAtom
