from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkxMeshSection import hkxMeshSection
from .hkxMeshUserChannelInfo import hkxMeshUserChannelInfo


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxMesh(hkReferencedObject):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(16, "sections", hkArray(Ptr(hkxMeshSection))),
        Member(32, "userChannelInfos", hkArray(Ptr(hkxMeshUserChannelInfo))),
    )
    members = hkReferencedObject.members + local_members

    sections: list[hkxMeshSection]
    userChannelInfos: list[hkxMeshUserChannelInfo]
