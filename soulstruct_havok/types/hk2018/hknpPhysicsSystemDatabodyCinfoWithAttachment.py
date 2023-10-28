from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hknpBodyCinfo import hknpBodyCinfo


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpPhysicsSystemDatabodyCinfoWithAttachment(hknpBodyCinfo):
    alignment = 16
    byte_size = 176
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2386517457
    __real_name = "hknpPhysicsSystemData::bodyCinfoWithAttachment"

    local_members = (
        Member(164, "attachedBody", _int),
    )
    members = hknpBodyCinfo.members + local_members

    attachedBody: int
