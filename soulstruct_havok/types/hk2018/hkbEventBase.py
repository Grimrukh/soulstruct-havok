from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkbEventPayload import hkbEventPayload


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbEventBase(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "id", hkInt32),
        Member(8, "payload", Ptr(hkbEventPayload)),
    )
    members = local_members

    id: int
    payload: hkbEventPayload