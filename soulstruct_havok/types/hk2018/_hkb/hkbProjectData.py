from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *

from .hkbProjectStringData import hkbProjectStringData
from .hkbTransitionEffectEventMode import hkbTransitionEffectEventMode


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbProjectData(hkReferencedObject):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 1280364313
    __version = 2

    local_members = (
        Member(32, "worldUpWS", hkVector4),
        Member(48, "stringData", hkRefPtr(hkbProjectStringData, hsh=2168375972)),
        Member(56, "defaultEventMode", hkEnum(hkbTransitionEffectEventMode, hkInt8)),
    )
    members = hkReferencedObject.members + local_members

    worldUpWS: hkVector4
    stringData: hkbProjectStringData
    defaultEventMode: hkbTransitionEffectEventMode
