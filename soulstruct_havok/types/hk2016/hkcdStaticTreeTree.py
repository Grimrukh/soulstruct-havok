from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkAabb import hkAabb
from .hkcdStaticTreeDynamicStorage import hkcdStaticTreeDynamicStorage


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkcdStaticTreeTree(hkcdStaticTreeDynamicStorage):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkcdStaticTree::Tree"

    local_members = (
        Member(16, "domain", hkAabb),
    )
    members = hkcdStaticTreeDynamicStorage.members + local_members

    domain: hkAabb

    __templates = (
        TemplateType("tSTORAGE", _type=hkcdStaticTreeDynamicStorage),
    )
