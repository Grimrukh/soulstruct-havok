from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hkaBoneAttachment(hkReferencedObject):
    alignment = 16
    byte_size = 128
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member(24, "originalSkeletonName", hkStringPtr),
        Member(32, "boneFromAttachment", hkMatrix4),
        Member(96, "attachment", hkRefVariant(hkReferencedObject, hsh=340571500)),
        Member(104, "name", hkStringPtr),
        Member(112, "boneIndex", hkInt16),
    )
    members = hkReferencedObject.members + local_members

    originalSkeletonName: hkStringPtr
    boneFromAttachment: hkMatrix4
    attachment: hkReferencedObject
    name: hkStringPtr
    boneIndex: int
