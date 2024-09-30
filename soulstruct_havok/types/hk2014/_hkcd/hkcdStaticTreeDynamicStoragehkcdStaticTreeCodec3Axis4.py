from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkcdStaticTreeCodec3Axis4 import hkcdStaticTreeCodec3Axis4


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkcdStaticTreeDynamicStoragehkcdStaticTreeCodec3Axis4(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 667684532

    local_members = (
        Member(0, "nodes", hkArray(hkcdStaticTreeCodec3Axis4)),
    )
    members = local_members

    nodes: list[hkcdStaticTreeCodec3Axis4]
