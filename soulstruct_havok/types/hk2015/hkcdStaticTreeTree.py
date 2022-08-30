from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


from .hkcdStaticTreeDynamicStorage import hkcdStaticTreeDynamicStorage
from .hkAabb import hkAabb


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
        TemplateType("tSTORAGE", type=hkcdStaticTreeDynamicStorage),
    )
