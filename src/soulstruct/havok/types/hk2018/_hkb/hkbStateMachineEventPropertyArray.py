from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkbEventProperty import hkbEventProperty


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbStateMachineEventPropertyArray(hkReferencedObject):
    alignment = 8
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkbStateMachine::EventPropertyArray"

    local_members = (
        Member(24, "events", hkArray(hkbEventProperty)),
    )
    members = hkReferencedObject.members + local_members

    events: list[hkbEventProperty]
