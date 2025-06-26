from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkaiAnnotatedStreamingSetSide import hkaiAnnotatedStreamingSetSide
from .hkaiStreamingSet import hkaiStreamingSet


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaiAnnotatedStreamingSet(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "side", hkEnum(hkaiAnnotatedStreamingSetSide, hkUint8)),
        Member(8, "streamingSet", hkRefPtr(hkaiStreamingSet)),
    )
    members = local_members

    side: hkaiAnnotatedStreamingSetSide
    streamingSet: hkaiStreamingSet
