from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hkDefaultPropertyBag(hk):
    alignment = 8
    byte_size = 72
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(0, "propertyMap", hkHashMap, MemberFlags.Protected),
        Member(32, "transientPropertyMap", hkHashMap, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(64, "locked", _bool, MemberFlags.NotSerializable),
    )
    members = local_members

    propertyMap: hkHashMap
    transientPropertyMap: hkHashMap
    locked: bool
