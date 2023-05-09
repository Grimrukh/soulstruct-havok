from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkaAnimation import hkaAnimation


@dataclass(slots=True, eq=False, repr=False)
class hkaInterleavedUncompressedAnimation(hkaAnimation):
    alignment = 8
    byte_size = 72
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3449291259

    local_members = (
        Member(40, "transforms", hkArray(hkQsTransform), MemberFlags.Private),
        Member(52, "floats", hkArray(hkReal), MemberFlags.Private),
    )
    members = hkaAnimation.members + local_members

    transforms: list[hkQsTransform]
    numBlocks: list[float]
