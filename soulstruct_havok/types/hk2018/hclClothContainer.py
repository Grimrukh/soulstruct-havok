from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *

from .hclCollidable import hclCollidable
from .hclClothData import hclClothData


@dataclass(slots=True, eq=False, repr=False)
class hclClothContainer(hkReferencedObject):
    alignment = 8
    byte_size = 56
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 829381375
    __version = 1

    local_members = (
        Member(24, "collidables", hkArray(hkRefPtr(hclCollidable))),
        Member(40, "clothDatas", hkArray(hkRefPtr(hclClothData, hsh=1749100557), hsh=1122004664)),
    )
    members = hkReferencedObject.members + local_members

    collidables: list[hclCollidable]
    clothDatas: list[hclClothData]
