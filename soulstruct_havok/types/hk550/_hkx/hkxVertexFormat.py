from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxVertexFormat(hk):
    alignment = 1
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 933220756

    local_members = (
        Member(0, "stride", hkUint8),
        Member(1, "positionOffset", hkUint8),
        Member(2, "normalOffset", hkUint8),
        Member(3, "tangentOffset", hkUint8),
        Member(4, "binormalOffset", hkUint8),
        Member(5, "numBonesPerVertex", hkUint8),
        Member(6, "boneIndexOffset", hkUint8),
        Member(7, "boneWeightOffset", hkUint8),
        Member(8, "numTextureChannels", hkUint8),
        Member(9, "tFloatCoordOffset", hkUint8),
        Member(10, "tQuantizedCoordOffset", hkUint8),
        Member(11, "colorOffset", hkUint8),
    )
    members = local_members

    stride: int
    positionOffset: int
    normalOffset: int
    tangentOffset: int
    binormalOffset: int
    numBonesPerVertex: int
    boneIndexOffset: int
    boneWeightOffset: int
    numTextureChannels: int
    tFloatCoordOffset: int
    tQuantizedCoordOffset: int
    colorOffset: int
