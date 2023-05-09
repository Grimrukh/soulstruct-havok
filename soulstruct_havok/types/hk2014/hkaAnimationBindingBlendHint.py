from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hkaAnimationBindingBlendHint(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int8
    __real_name = "hkaAnimationBinding::BlendHint"
    local_members = ()
