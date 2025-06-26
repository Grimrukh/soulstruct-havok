from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkaSkeletonMapperData import hkaSkeletonMapperData


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaSkeletonMapper(hkReferencedObject):
    alignment = 16
    byte_size = 192
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2900984988

    local_members = (
        Member(16, "mapping", hkaSkeletonMapperData),
    )
    members = hkReferencedObject.members + local_members

    mapping: hkaSkeletonMapperData
