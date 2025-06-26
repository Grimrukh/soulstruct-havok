from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkxMeshSection import hkxMeshSection
from .hkxMeshUserChannelInfo import hkxMeshUserChannelInfo


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxMesh(hk):
    alignment = 4
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1927866441

    local_members = (
        Member(0, "sections", SimpleArray(Ptr(hkxMeshSection))),
        Member(8, "userChannelInfos", SimpleArray(hkxMeshUserChannelInfo)),
    )
    members = local_members

    sections: list[hkxMeshSection]
    userChannelInfos: list[hkxMeshUserChannelInfo]
