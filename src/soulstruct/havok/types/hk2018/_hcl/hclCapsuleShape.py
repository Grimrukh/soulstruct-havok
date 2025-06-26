from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hclShape import hclShape


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclCapsuleShape(hclShape):
    alignment = 16
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 2376887643
    __version = 1

    local_members = (
        Member(32, "start", hkVector4, MemberFlags.Protected),
        Member(48, "end", hkVector4, MemberFlags.Protected),
        Member(64, "dir", hkVector4, MemberFlags.Protected),
        Member(80, "radius", hkReal, MemberFlags.Protected),
        Member(84, "capLenSqrdInv", hkReal, MemberFlags.Protected),
    )
    members = hclShape.members + local_members

    start: Vector4
    end: Vector4
    dir: Vector4
    radius: float
    capLenSqrdInv: float
