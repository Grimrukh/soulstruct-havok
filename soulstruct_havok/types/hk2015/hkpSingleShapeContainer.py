from __future__ import annotations

from soulstruct_havok.enums import *
from soulstruct_havok.types.core import *
from .hkpShape import hkpShape
from .hkpShapeContainer import hkpShapeContainer


class hkpSingleShapeContainer(hkpShapeContainer):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "childShape", Ptr(hkpShape, hsh=1200505464), MemberFlags.Protected),
    )
    members = hkpShapeContainer.members + local_members

    childShape: hkpShape
