from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hclConstraintSet import hclConstraintSet
from .hclLocalRangeConstraintSetLocalConstraint import hclLocalRangeConstraintSetLocalConstraint


from .hclLocalRangeConstraintSetShapeType import hclLocalRangeConstraintSetShapeType



class hclLocalRangeConstraintSet(hclConstraintSet):
    alignment = 8
    byte_size = 72
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3497046835
    __version = 3

    local_members = (
        Member(40, "localConstraints", hkArray(hclLocalRangeConstraintSetLocalConstraint, hsh=2932720944)),
        Member(56, "referenceMeshBufferIdx", hkUint32),
        Member(60, "stiffness", hkReal),
        Member(64, "shapeType", hkEnum(hclLocalRangeConstraintSetShapeType, hkUint32)),
        Member(68, "applyNormalComponent", hkBool),
    )
    members = hclConstraintSet.members + local_members

    localConstraints: list[hclLocalRangeConstraintSetLocalConstraint]
    referenceMeshBufferIdx: int
    stiffness: float
    shapeType: hclLocalRangeConstraintSetShapeType
    applyNormalComponent: bool
