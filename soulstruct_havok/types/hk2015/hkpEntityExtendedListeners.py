from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkpEntitySmallArraySerializeOverrideType import hkpEntitySmallArraySerializeOverrideType


@dataclass(slots=True, eq=False, repr=False)
class hkpEntityExtendedListeners(hk):
    alignment = 8
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkpEntity::ExtendedListeners"

    local_members = (
        Member(0, "activationListeners", hkpEntitySmallArraySerializeOverrideType, MemberFlags.NotSerializable),
        Member(16, "entityListeners", hkpEntitySmallArraySerializeOverrideType, MemberFlags.NotSerializable),
    )
    members = local_members

    activationListeners: hkpEntitySmallArraySerializeOverrideType
    entityListeners: hkpEntitySmallArraySerializeOverrideType
