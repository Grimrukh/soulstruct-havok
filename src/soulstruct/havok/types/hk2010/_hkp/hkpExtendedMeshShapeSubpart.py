from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpExtendedMeshShapeSubpart(hk):
    alignment = 8
    byte_size = 20
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __real_name = "hkpExtendedMeshShape::Subpart"

    # TODO: adjusted
    local_members = (
        Member(0, "typeAndFlags", hkUint16, MemberFlags.Protected),
        Member(2, "shapeInfo", hkUint16),
        Member(4, "materialStriding", hkInt16, MemberFlags.NotSerializable),
        Member(6, "materialIndexStriding", hkUint16),
        Member(8, "materialIndexBase", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(12, "materialBase", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(16, "userData", hkUint32),
    )
    members = local_members

    typeAndFlags: int
    shapeInfo: int
    materialStriding: int
    materialIndexStriding: int
    materialIndexBase: None = None
    materialBase: None = None
    userData: int
