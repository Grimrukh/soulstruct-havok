from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaBoneAttachment(hkReferencedObject):
    alignment = 16
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "originalSkeletonName", hkStringPtr),
        Member(16, "boneFromAttachment", hkMatrix4),
        Member(80, "attachment", Ptr(hkReferencedObject)),
        Member(84, "name", hkStringPtr),
        Member(88, "boneIndex", hkInt16),
    )
    members = hkReferencedObject.members + local_members

    originalSkeletonName: str
    boneFromAttachment: hkMatrix4
    attachment: hkReferencedObject
    name: str
    boneIndex: int
