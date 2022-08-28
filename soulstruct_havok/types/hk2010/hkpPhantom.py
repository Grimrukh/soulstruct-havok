from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hkpWorldObject import hkpWorldObject


class hkpPhantom(hkpWorldObject):
    alignment = 16
    byte_size = 164
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(140, "overlapListeners", hkArray(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(152, "phantomListeners", hkArray(hkReflectDetailOpaque), MemberFlags.NotSerializable),
    )
    members = hkpWorldObject.members + local_members

    overlapListeners: list
    phantomListeners: list