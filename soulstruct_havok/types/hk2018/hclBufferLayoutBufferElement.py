from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hclRuntimeConversionInfoVectorConversion import hclRuntimeConversionInfoVectorConversion


@dataclass(slots=True, eq=False, repr=False)
class hclBufferLayoutBufferElement(hk):
    alignment = 1
    byte_size = 4
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hclBufferLayout::BufferElement"

    local_members = (
        Member(0, "vectorConversion", hkEnum(hclRuntimeConversionInfoVectorConversion, hkUint8)),
        Member(1, "vectorSize", hkUint8),
        Member(2, "slotId", hkUint8),
        Member(3, "slotStart", hkUint8),
    )
    members = local_members

    vectorConversion: hclRuntimeConversionInfoVectorConversion
    vectorSize: int
    slotId: int
    slotStart: int
