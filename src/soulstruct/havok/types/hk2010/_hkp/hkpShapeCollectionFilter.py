from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpShapeCollectionFilter(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    local_members = ()
