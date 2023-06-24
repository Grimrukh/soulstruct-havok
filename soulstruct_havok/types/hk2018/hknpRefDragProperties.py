from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *

from .hknpDragProperties import hknpDragProperties


@dataclass(slots=True, eq=False, repr=False)
class hknpRefDragProperties(hkReferencedObject):
    alignment = 16
    byte_size = 224
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1462315717

    local_members = (
        Member(32, "dragProperties", hknpDragProperties),
    )
    members = hkReferencedObject.members + local_members

    dragProperties: hknpDragProperties
