from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .._hkcd.hkcdShape import hkcdShape


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpShapeBase(hkcdShape):
    alignment = 8
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    local_members = ()
