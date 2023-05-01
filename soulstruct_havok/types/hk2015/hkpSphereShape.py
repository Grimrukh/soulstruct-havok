from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


from .hkpConvexShape import hkpConvexShape


class hkpSphereShape(hkpConvexShape):
    alignment = 8
    byte_size = 56
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2171905039

    local_members = (
        Member(40, "pad16", hkGenericStruct(hkUint32, 3), MemberFlags.NotSerializable),
    )
    members = hkpConvexShape.members + local_members

    pad16: tuple[int]