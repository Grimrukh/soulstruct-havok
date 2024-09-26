from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


from .hkbNode import hkbNode
from .hkbGeneratorPartitionInfo import hkbGeneratorPartitionInfo


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbGenerator(hkbNode):
    alignment = 8
    byte_size = 152
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member(
            96,
            "partitionInfo",
            hkbGeneratorPartitionInfo,
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(136, "syncInfo", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(144, "pad", hkGenericStruct(hkInt8, 4), MemberFlags.NotSerializable | MemberFlags.Private),
    )
    members = hkbNode.members + local_members

    partitionInfo: hkbGeneratorPartitionInfo
    syncInfo: hkReflectDetailOpaque
    pad: tuple[hkInt8]
