from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *

from .hkpMoppCodeCodeInfo import hkpMoppCodeCodeInfo
from .hkpMoppCodeBuildType import hkpMoppCodeBuildType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpMoppCode(hkReferencedObject):
    alignment = 16
    byte_size = 44
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "info", hkpMoppCodeCodeInfo),
        Member(32, "data", hkArray(hkUint8, hsh=2877151166)),
    )
    members = hkReferencedObject.members + local_members

    info: hkpMoppCodeCodeInfo
    data: list[int]
