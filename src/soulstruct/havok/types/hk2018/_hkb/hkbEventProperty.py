from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkbEventBase import hkbEventBase


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbEventProperty(hkbEventBase):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1
    local_members = ()
