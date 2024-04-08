from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkcdStaticAabbTreeImpl import hkcdStaticAabbTreeImpl


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkcdStaticAabbTree(hkReferencedObject):
    alignment = 8
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3304427880
    __version = 2

    local_members = (
        Member(24, "treePtr", hkRefPtr(hkcdStaticAabbTreeImpl, hsh=3749145323), MemberFlags.Protected),
    )
    members = hkReferencedObject.members + local_members

    treePtr: hkcdStaticAabbTreeImpl
