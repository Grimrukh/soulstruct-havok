from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkbCustomIdSelector import hkbCustomIdSelector


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class CustomPreDeleteIndexSelector(hkbCustomIdSelector):
    alignment = 8
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1979749018
    local_members = ()
