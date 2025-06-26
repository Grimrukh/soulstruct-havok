from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from .core import *

from ._hkp.hkpBvTreeShape import hkpBvTreeShape
from ._hkp.hkpMoppCode import hkpMoppCode


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkMoppBvTreeShapeBase(hkpBvTreeShape):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57

    # TODO: adjusted
    local_members = (
        Member(20, "code", Ptr(hkpMoppCode)),
        Member(24, "moppData", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(28, "moppDataSize", hkUint32, MemberFlags.NotSerializable),
        Member(32, "codeInfoCopy", hkVector4, MemberFlags.NotSerializable),
    )

    members = hkpBvTreeShape.members + local_members

    code: hkpMoppCode
    moppData: None = None
    moppDataSize: int
    codeInfoCopy: Vector4
