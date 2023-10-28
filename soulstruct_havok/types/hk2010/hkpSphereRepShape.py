from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkpShape import hkpShape


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpSphereRepShape(hkpShape):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    local_members = ()
