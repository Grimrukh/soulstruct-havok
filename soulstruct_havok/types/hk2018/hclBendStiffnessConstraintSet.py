from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hclConstraintSet import hclConstraintSet
from .hclBendStiffnessConstraintSetLink import hclBendStiffnessConstraintSetLink


class hclBendStiffnessConstraintSet(hclConstraintSet):
    alignment = 8
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 1747957381
    __version = 2

    local_members = (
        Member(40, "links", hkArray(hclBendStiffnessConstraintSetLink, hsh=1918745169)),
        Member(56, "maxRestPoseHeightSq", hkReal),
        Member(60, "clampBendStiffness", hkBool),
        Member(61, "useRestPoseConfig", hkBool),
    )
    members = hclConstraintSet.members + local_members

    links: list[hclBendStiffnessConstraintSetLink]
    maxRestPoseHeightSq: float
    clampBendStiffness: bool
    useRestPoseConfig: bool