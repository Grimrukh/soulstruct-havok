from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaiUserEdgeUtilsObb(hk):
    alignment = 16
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkaiUserEdgeUtils::Obb"

    local_members = (
        Member(0, "transform", hkTransform),
        Member(64, "halfExtents", hkVector4),
    )
    members = local_members

    transform: hkTransform
    halfExtents: hkVector4
