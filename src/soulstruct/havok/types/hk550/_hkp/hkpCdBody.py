from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkpShape import hkpShape


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpCdBody(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "shape", Ptr(hkpShape)),
        Member(4, "shapeKey", hkUint32),
        Member(8, "motion", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(12, "parent", Ptr(DefType("hkpCdBody", lambda: hkpCdBody)), MemberFlags.NotSerializable),
    )
    members = local_members

    shape: hkpShape
    shapeKey: int
    motion: None
    parent: hkpCdBody
