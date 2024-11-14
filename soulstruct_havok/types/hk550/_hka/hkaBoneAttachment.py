from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaBoneAttachment(hkReferencedObject):
    alignment = 16
    byte_size = 92
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2346532506

    local_members = (
        Member(16, "boneFromAttachment", hkMatrix4),
        Member(80, "attachment", Ptr(hkReferencedObject)),
        Member(84, "name", hkStringPtr),
        Member(88, "boneIndex", hkInt16),
    )
    members = hkReferencedObject.members + local_members

    boneFromAttachment: hkMatrix4
    attachment: hkReferencedObject
    name: str
    boneIndex: int
