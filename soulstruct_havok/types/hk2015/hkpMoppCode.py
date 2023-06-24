from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkpMoppCodeCodeInfo import hkpMoppCodeCodeInfo
from .hkpMoppCodeBuildType import hkpMoppCodeBuildType


@dataclass(slots=True, eq=False, repr=False)
class hkpMoppCode(hkReferencedObject):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1660805132

    local_members = (
        Member(16, "info", hkpMoppCodeCodeInfo),
        Member(32, "data", hkArray(hkUint8, hsh=2877151166)),
        Member(48, "buildType", hkEnum(hkpMoppCodeBuildType, hkInt8)),
    )
    members = hkReferencedObject.members + local_members

    info: hkpMoppCodeCodeInfo
    data: list[int]
    buildType: hkpMoppCodeBuildType
