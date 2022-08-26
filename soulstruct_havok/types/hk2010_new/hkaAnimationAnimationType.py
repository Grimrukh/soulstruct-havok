from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


class hkaAnimationAnimationType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32
    __real_name = "hkaAnimation::AnimationType"
    local_members = ()
