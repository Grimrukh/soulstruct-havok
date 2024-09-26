from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *

from .hkpShape import hkpShape
from .hkpShapeContainer import hkpShapeContainer


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpShapeCollection(hkpShape):
    alignment = 8
    byte_size = 20
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 121

    # TODO: confident for Havok 5.5.0
    local_members = (
        Member(16, "disableWelding", hkBool),
    )
    members = hkpShape.members + local_members

    disableWelding: bool

    __interfaces = (
        Interface(hkpShapeContainer, flags=32),
    )
