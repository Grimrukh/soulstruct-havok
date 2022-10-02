from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hkaAnimation import hkaAnimation


class hkaInterleavedUncompressedAnimation(hkaAnimation):
    alignment = 8
    byte_size = 88
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3449291259  # TODO: may be wrong for 2015 (from TagTools; could be 2014 only)

    local_members = (
        Member(56, "transforms", hkArray(hkQsTransform), MemberFlags.Private),
        Member(72, "floats", hkArray(hkReal), MemberFlags.Private),
    )
    members = hkaAnimation.members + local_members

    transforms: list[hkQsTransform]
    numBlocks: list[float]
