from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclTransformSetDefinition(hkReferencedObject):
    alignment = 8
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 456237410

    local_members = (
        Member(24, "name", hkStringPtr),
        Member(32, "type", hkInt32),
        Member(36, "numTransforms", hkUint32),
    )
    members = hkReferencedObject.members + local_members

    name: hkStringPtr
    type: int
    numTransforms: int
