from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkpConstraintAtom import hkpConstraintAtom
from .hkpConeLimitConstraintAtomMeasurementMode import hkpConeLimitConstraintAtomMeasurementMode


@dataclass(slots=True, eq=False, repr=False)
class hkpConeLimitConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 20
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(2, "isEnabled", hkUint8),
        Member(3, "twistAxisInA", hkUint8),
        Member(4, "refAxisInB", hkUint8),
        Member(5, "angleMeasurementMode", hkEnum(hkpConeLimitConstraintAtomMeasurementMode, hkUint8)),
        Member(6, "memOffsetToAngleOffset", hkUint8),
        Member(8, "minAngle", hkReal),
        Member(12, "maxAngle", hkReal),
        Member(16, "angularLimitsTauFactor", hkReal),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: int
    twistAxisInA: int
    refAxisInB: int
    angleMeasurementMode: int
    memOffsetToAngleOffset: int
    minAngle: float
    maxAngle: float
    angularLimitsTauFactor: float
