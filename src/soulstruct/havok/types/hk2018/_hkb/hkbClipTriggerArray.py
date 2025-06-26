from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkbClipTrigger import hkbClipTrigger


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbClipTriggerArray(hkReferencedObject):
    alignment = 8
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(24, "triggers", hkArray(hkbClipTrigger)),
    )
    members = hkReferencedObject.members + local_members

    triggers: list[hkbClipTrigger]
