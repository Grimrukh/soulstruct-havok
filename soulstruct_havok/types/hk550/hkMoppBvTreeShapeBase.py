from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *

from .hkpBvTreeShape import hkpBvTreeShape
from .hkpMoppCode import hkpMoppCode


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkMoppBvTreeShapeBase(hkpBvTreeShape):
    alignment = 16
    byte_size = 44
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57

    local_members = (
        Member(16, "code", Ptr(hkpMoppCode)),
        Member(20, "moppData", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(24, "moppDataSize", hkUint32, MemberFlags.NotSerializable),
        Member(28, "codeInfoCopy", hkVector4, MemberFlags.NotSerializable),
    )

    members = hkpBvTreeShape.members + local_members

    code: hkpMoppCode
    moppData: None = None
    moppDataSize: int = 0
    codeInfoCopy: Vector4
