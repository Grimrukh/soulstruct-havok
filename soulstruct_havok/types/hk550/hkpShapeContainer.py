from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpShapeContainer(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    local_members = ()
