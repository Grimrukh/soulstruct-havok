from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


from .hkbBindable import hkbBindable
from .hkbGenerator import hkbGenerator
from .hkbBoneWeightArray import hkbBoneWeightArray


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbBlenderGeneratorChild(hkbBindable):
    alignment = 16
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 4272564306
    __version = 2

    local_members = (
        Member(64, "generator", Ptr(hkbGenerator, hsh=389751017)),
        Member(72, "boneWeights", hkRefPtr(hkbBoneWeightArray)),
        Member(80, "weight", hkReal),
        Member(84, "worldFromModelWeight", hkReal),
    )
    members = hkbBindable.members + local_members

    generator: hkbGenerator
    boneWeights: hkbBoneWeightArray
    weight: float
    worldFromModelWeight: float
