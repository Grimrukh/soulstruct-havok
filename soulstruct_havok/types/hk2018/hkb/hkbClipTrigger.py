from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


from .hkbEventProperty import hkbEventProperty


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbClipTrigger(hk):
    alignment = 8
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(0, "localTime", hkReal),
        Member(8, "event", hkbEventProperty),
        Member(24, "relativeToEndOfClip", hkBool),
        Member(25, "acyclic", hkBool),
        Member(26, "isAnnotation", hkBool),
    )
    members = local_members

    localTime: float
    event: hkbEventProperty
    relativeToEndOfClip: bool
    acyclic: bool
    isAnnotation: bool
