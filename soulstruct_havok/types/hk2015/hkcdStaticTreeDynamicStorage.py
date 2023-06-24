from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkcdStaticTreeCodec3Axis6 import hkcdStaticTreeCodec3Axis6


@dataclass(slots=True, eq=False, repr=False)
class hkcdStaticTreeDynamicStorage(hk):
    alignment = 4
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkcdStaticTree::DynamicStorage"

    local_members = (
        Member(0, "nodes", hkArray(hkcdStaticTreeCodec3Axis6)),
    )
    members = local_members

    nodes: list[hkcdStaticTreeCodec3Axis6]

    __templates = (
        TemplateType("tCODEC", type=hkcdStaticTreeCodec3Axis6),
    )
