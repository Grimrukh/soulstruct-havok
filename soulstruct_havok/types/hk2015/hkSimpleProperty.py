from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkSimplePropertyValue import hkSimplePropertyValue


@dataclass(slots=True, eq=False, repr=False)
class hkSimpleProperty(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member(0, "key", hkUint32),
        Member(4, "alignmentPadding", hkUint32, MemberFlags.NotSerializable),
        Member(8, "value", hkSimplePropertyValue),
    )
    members = local_members

    key: int
    alignmentPadding: int
    value: hkSimplePropertyValue
