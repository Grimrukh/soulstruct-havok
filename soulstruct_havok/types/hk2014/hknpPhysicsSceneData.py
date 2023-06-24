from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hknpPhysicsSystemData import hknpPhysicsSystemData
from .hknpRefWorldCinfo import hknpRefWorldCinfo


@dataclass(slots=True, eq=False, repr=False)
class hknpPhysicsSceneData(hkReferencedObject):
    alignment = 16
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1880942380
    __version = 1

    local_members = (
        Member(16, "systemDatas", hkArray(Ptr(hknpPhysicsSystemData))),
        Member(32, "worldCinfo", Ptr(hknpRefWorldCinfo)),
    )
    members = hkReferencedObject.members + local_members

    systemDatas: list[hknpPhysicsSystemData]
    worldCinfo: hknpRefWorldCinfo
