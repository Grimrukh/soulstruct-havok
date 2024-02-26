from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbGeneratorPartitionInfo(hk):
    alignment = 4
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "boneMask", hkGenericStruct(hkUint32, 8), MemberFlags.Private),
        Member(32, "partitionMask", hkGenericStruct(hkUint32, 1), MemberFlags.Private),
        Member(36, "numBones", hkInt16, MemberFlags.Private),
        Member(38, "numMaxPartitions", hkInt16, MemberFlags.Private),
    )
    members = local_members

    boneMask: tuple[hkUint32]
    partitionMask: tuple[hkUint32]
    numBones: int
    numMaxPartitions: int
