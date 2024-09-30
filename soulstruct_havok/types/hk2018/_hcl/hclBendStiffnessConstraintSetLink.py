from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclBendStiffnessConstraintSetLink(hk):
    alignment = 4
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 275062867
    __version = 1
    __real_name = "hclBendStiffnessConstraintSet::Link"

    local_members = (
        Member(0, "weightA", hkReal),
        Member(4, "weightB", hkReal),
        Member(8, "weightC", hkReal),
        Member(12, "weightD", hkReal),
        Member(16, "bendStiffness", hkReal),
        Member(20, "restCurvature", hkReal),
        Member(24, "particleA", hkUint16),
        Member(26, "particleB", hkUint16),
        Member(28, "particleC", hkUint16),
        Member(30, "particleD", hkUint16),
    )
    members = local_members

    weightA: float
    weightB: float
    weightC: float
    weightD: float
    bendStiffness: float
    restCurvature: float
    particleA: int
    particleB: int
    particleC: int
    particleD: int
