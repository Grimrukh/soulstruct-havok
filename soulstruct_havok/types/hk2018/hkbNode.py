from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkbBindable import hkbBindable
from .hkbNodeCloneState import hkbNodeCloneState
from .hkbNodeType import hkbNodeType
from .hkbVerifiable import hkbVerifiable


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbNode(hkbBindable):
    alignment = 8
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 109
    __version = 1

    local_members = (
        Member(64, "userData", hkUlong),
        Member(72, "name", hkStringPtr),
        Member(80, "id", hkUint16, MemberFlags.NotSerializable),
        Member(
            82,
            "cloneState",
            hkEnum(hkbNodeCloneState, hkInt8),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(83, "type", hkEnum(hkbNodeType, hkUint8), MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(88, "nodeInfo", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
    )
    members = hkbBindable.members + local_members

    userData: int
    name: hkStringPtr
    id: int
    cloneState: hkbNodeCloneState
    type: hkbNodeType
    nodeInfo: hkReflectDetailOpaque

    __interfaces = (
        Interface(hkbVerifiable, flags=56),
    )
