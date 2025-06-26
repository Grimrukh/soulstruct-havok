from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkcdStaticTreeCodec3Axis5 import hkcdStaticTreeCodec3Axis5


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkcdStaticTreeDynamicStoragehkcdStaticTreeCodec3Axis5(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 153534671

    local_members = (
        Member(0, "nodes", hkArray(hkcdStaticTreeCodec3Axis5)),
    )
    members = local_members

    nodes: list[hkcdStaticTreeCodec3Axis5]
