from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class CustomMeshParameter(hkReferencedObject):
    alignment = 8
    byte_size = 72
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 4160631638

    local_members = (
        Member(16, "version", hkUint32, MemberFlags.Private),
        Member(24, "vertexDataBuffer", hkArray(hkUint8, hsh=2877151166), MemberFlags.Private),
        Member(40, "vertexDataStride", hkInt32, MemberFlags.Private),
        Member(48, "primitiveDataBuffer", hkArray(hkUint8, hsh=2877151166), MemberFlags.Private),
        Member(64, "materialNameData", hkUint32, MemberFlags.Private),
    )
    members = hkReferencedObject.members + local_members

    version: int
    vertexDataBuffer: list[int]
    vertexDataStride: int
    primitiveDataBuffer: list[int]
    materialNameData: int
