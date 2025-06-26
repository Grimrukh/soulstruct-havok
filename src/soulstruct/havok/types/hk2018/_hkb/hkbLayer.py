from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkbBindable import hkbBindable
from .hkbGenerator import hkbGenerator
from .hkbBoneWeightArray import hkbBoneWeightArray
from .hkbEventDrivenBlendingObject import hkbEventDrivenBlendingObject


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbLayer(hkbBindable):
    alignment = 16
    byte_size = 128
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 516885449
    __version = 2

    local_members = (
        Member(64, "generator", hkRefPtr(hkbGenerator, hsh=1798718120)),
        Member(72, "boneWeights", hkRefPtr(hkbBoneWeightArray)),
        Member(80, "useMotion", hkBool),
        Member(84, "blendingControlData", hkbEventDrivenBlendingObject),
    )
    members = hkbBindable.members + local_members

    generator: hkbGenerator
    boneWeights: hkbBoneWeightArray
    useMotion: bool
    blendingControlData: hkbEventDrivenBlendingObject
