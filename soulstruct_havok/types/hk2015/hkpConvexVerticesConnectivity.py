from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hkpConvexVerticesConnectivity(hkReferencedObject):
    alignment = 8
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3392747697

    local_members = (
        Member(16, "vertexIndices", hkArray(hkUint16, hsh=3551656838)),
        Member(32, "numVerticesPerFace", hkArray(hkUint8, hsh=2877151166)),
    )
    members = hkReferencedObject.members + local_members

    vertexIndices: list[int]
    numVerticesPerFace: list[int]
