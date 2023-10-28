from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *

from .hclTransformSetUsageTransformTracker import hclTransformSetUsageTransformTracker


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclTransformSetUsage(hk):
    alignment = 8
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(0, "perComponentFlags", hkGenericStruct(hkUint8, 2)),
        Member(
            8,
            "perComponentTransformTrackers",
            hkArray(hclTransformSetUsageTransformTracker, hsh=3120187409),
        ),
    )
    members = local_members

    perComponentFlags: tuple[hkUint8]
    perComponentTransformTrackers: list[hclTransformSetUsageTransformTracker]
