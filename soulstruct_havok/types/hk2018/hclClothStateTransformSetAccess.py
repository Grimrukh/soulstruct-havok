from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *

from .hclTransformSetUsage import hclTransformSetUsage


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclClothStateTransformSetAccess(hk):
    alignment = 8
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 951141832
    __real_name = "hclClothState::TransformSetAccess"

    local_members = (
        Member(0, "transformSetIndex", hkUint32),
        Member(8, "transformSetUsage", hclTransformSetUsage),
    )
    members = local_members

    transformSetIndex: int
    transformSetUsage: hclTransformSetUsage
