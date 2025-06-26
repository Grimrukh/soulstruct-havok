from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkcdStaticTreeAabb6BytesTree import hkcdStaticTreeAabb6BytesTree


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkcdStaticAabbTreeImpl(hkReferencedObject):
    alignment = 16
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 1906751376
    __version = 1
    __real_name = "hkcdStaticAabbTree::Impl"

    local_members = (
        Member(32, "tree", hkcdStaticTreeAabb6BytesTree),
    )
    members = hkReferencedObject.members + local_members

    tree: hkcdStaticTreeAabb6BytesTree
