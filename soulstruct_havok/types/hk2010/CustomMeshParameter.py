from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class CustomMeshParameter(hkReferencedObject):
    alignment = 8
    byte_size = 48  # TODO: confirmed
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    # TODO: Had to rearrange these from 2015 to make sense. Maybe QLOC swapped the order? They had to recompile the
    #  Havok files at some point.
    local_members = (
        Member(8, "version", hkUint32, MemberFlags.Private),
        Member(12, "vertexDataBuffer", hkArray(hkUint8), MemberFlags.Private),
        Member(24, "zero0", hkInt32, MemberFlags.Private),  # ?
        Member(28, "zero1", hkInt32, MemberFlags.Private),  # ?
        Member(32, "materialNameData", hkUint32, MemberFlags.Private),  # definitely here
        Member(36, "primitiveDataBuffer", hkArray(hkUint8), MemberFlags.Private),  # only place it fits! (empty anyway)
    )
    members = hkReferencedObject.members + local_members

    version: int
    vertexDataBuffer: list[int]
    zero0: int
    zero1: int
    materialNameData: int
    primitiveDataBuffer: list[int]
