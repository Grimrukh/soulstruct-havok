from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *

from .hkpBvTreeShape import hkpBvTreeShape
from .hkpMoppCode import hkpMoppCode


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkMoppBvTreeShapeBase(hkpBvTreeShape):
    alignment = 16
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member(40, "code", Ptr(hkpMoppCode, hsh=3878741831)),
        Member(48, "moppData", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(56, "moppDataSize", hkUint32, MemberFlags.NotSerializable),
        Member(64, "codeInfoCopy", hkVector4, MemberFlags.NotSerializable),
    )
    members = hkpBvTreeShape.members + local_members

    code: hkpMoppCode
    moppData: hkReflectDetailOpaque
    moppDataSize: int
    codeInfoCopy: Vector4
