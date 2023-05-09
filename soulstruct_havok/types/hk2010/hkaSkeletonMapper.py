from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkaSkeletonMapperData import hkaSkeletonMapperData


@dataclass(slots=True, eq=False, repr=False)
class hkaSkeletonMapper(hkReferencedObject):
    alignment = 16
    byte_size = 128
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 316621477

    local_members = (
        Member(16, "mapping", hkaSkeletonMapperData),
    )
    members = hkReferencedObject.members + local_members

    mapping: hkaSkeletonMapperData
