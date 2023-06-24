from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkpShape import hkpShape


@dataclass(slots=True, eq=False, repr=False)
class hkpCdBody(hk):
    alignment = 8
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member(0, "shape", Ptr(hkpShape, hsh=1200505464)),
        Member(8, "shapeKey", _unsigned_int),
        Member(16, "motion", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable | MemberFlags.Private),
        Member(24, "parent", Ptr(DefType("hkpCdBody", lambda: hkpCdBody)), MemberFlags.NotSerializable),
    )
    members = local_members

    shape: hkpShape
    shapeKey: int
    motion: hkReflectDetailOpaque
    parent: hkpCdBody
