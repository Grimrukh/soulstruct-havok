from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hclBufferLayoutBufferElement import hclBufferLayoutBufferElement
from .hclBufferLayoutSlot import hclBufferLayoutSlot

from .hclBufferLayoutTriangleFormat import hclBufferLayoutTriangleFormat


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclBufferLayout(hk):
    alignment = 1
    byte_size = 26
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "elementsLayout", hkGenericStruct(hclBufferLayoutBufferElement, 4)),
        Member(16, "slots", hkGenericStruct(hclBufferLayoutSlot, 4)),
        Member(24, "numSlots", hkUint8),
        Member(25, "triangleFormat", hkEnum(hclBufferLayoutTriangleFormat, hkUint8)),
    )
    members = local_members

    elementsLayout: tuple[hclBufferLayoutBufferElement]
    slots: tuple[hclBufferLayoutSlot]
    numSlots: int
    triangleFormat: hclBufferLayoutTriangleFormat
