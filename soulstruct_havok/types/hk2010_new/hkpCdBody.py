from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkpShape import hkpShape
from .hkpCdBody import hkpCdBody


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
