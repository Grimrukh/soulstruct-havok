from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class CustomMeshParameter(hkReferencedObject):
    """NOTE: Same as Dark Souls: PTDE (but not DSR, which seems to have rearranged its members)."""

    alignment = 8
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "version", hkUint32, MemberFlags.Private),
        Member(12, "vertexDataBuffer", hkArray(hkUint8, flags=0, forced_capacity=1), MemberFlags.Private),
        Member(24, "zero0", hkUint32, MemberFlags.Private),  # ?
        Member(28, "zero1", hkUint32, MemberFlags.Private),  # ?
        Member(32, "materialNameData", hkUint32, MemberFlags.Private),  # definitely here
        # TODO: "primitiveDataBuffer" goes here as of DSR, but seems to be all zeroes here.
        Member(36, "zero2", hkUint32, MemberFlags.Private),  # ?
        Member(40, "zero3", hkUint32, MemberFlags.Private),  # ?
        Member(44, "zero4", hkUint32, MemberFlags.Private),  # ?
    )
    members = hkReferencedObject.members + local_members

    version: int
    vertexDataBuffer: list[int]
    zero0: int
    zero1: int
    materialNameData: int
    zero2: int
    zero3: int
    zero4: int
