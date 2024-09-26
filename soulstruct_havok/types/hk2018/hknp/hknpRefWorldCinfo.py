from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *

from .hknpWorldCinfo import hknpWorldCinfo


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpRefWorldCinfo(hkReferencedObject):
    alignment = 16
    byte_size = 336
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(32, "info", hknpWorldCinfo),
    )
    members = hkReferencedObject.members + local_members

    info: hknpWorldCinfo
