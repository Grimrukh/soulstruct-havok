from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


from .hkpConvexTransformShapeBase import hkpConvexTransformShapeBase


class hkpConvexTranslateShape(hkpConvexTransformShapeBase):
    alignment = 16
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 77613734

    local_members = (
        Member(64, "translation", hkVector4, MemberFlags.Protected),
    )
    members = hkpConvexTransformShapeBase.members + local_members

    translation: Vector4
