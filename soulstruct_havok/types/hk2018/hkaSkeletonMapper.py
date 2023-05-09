from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *

from .hkaSkeletonMapperData import hkaSkeletonMapperData


@dataclass(slots=True, eq=False, repr=False)
class hkaSkeletonMapper(hkReferencedObject):
    alignment = 16
    byte_size = 208
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 367461012

    local_members = (
        Member(32, "mapping", hkaSkeletonMapperData),
    )
    members = hkReferencedObject.members + local_members

    mapping: hkaSkeletonMapperData
