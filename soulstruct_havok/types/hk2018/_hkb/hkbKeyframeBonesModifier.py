from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


from .hkbModifier import hkbModifier
from .hkbKeyframeBonesModifierKeyframeInfo import hkbKeyframeBonesModifierKeyframeInfo
from .hkbBoneIndexArray import hkbBoneIndexArray


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbKeyframeBonesModifier(hkbModifier):
    alignment = 8
    byte_size = 128
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3725109804
    __version = 3

    local_members = (
        Member(104, "keyframeInfo", hkArray(hkbKeyframeBonesModifierKeyframeInfo, hsh=1980859217)),
        Member(120, "keyframedBonesList", hkRefPtr(hkbBoneIndexArray, hsh=2023124160)),
    )
    members = hkbModifier.members + local_members

    keyframeInfo: list[hkbKeyframeBonesModifierKeyframeInfo]
    keyframedBonesList: hkbBoneIndexArray
