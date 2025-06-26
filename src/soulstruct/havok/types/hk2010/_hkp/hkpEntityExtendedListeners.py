from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkpEntitySmallArraySerializeOverrideType import hkpEntitySmallArraySerializeOverrideType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpEntityExtendedListeners(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "activationListeners", hkpEntitySmallArraySerializeOverrideType, MemberFlags.NotSerializable),
        Member(8, "entityListeners", hkpEntitySmallArraySerializeOverrideType, MemberFlags.NotSerializable),
    )
    members = local_members

    activationListeners: hkpEntitySmallArraySerializeOverrideType
    entityListeners: hkpEntitySmallArraySerializeOverrideType
