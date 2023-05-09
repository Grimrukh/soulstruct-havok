from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hclObjectSpaceDeformerLocalBlockPNT import hclObjectSpaceDeformerLocalBlockPNT
from .hclObjectSpaceDeformerLocalBlockUnpackedPNT import hclObjectSpaceDeformerLocalBlockUnpackedPNT
from .hclObjectSpaceSkinOperator import hclObjectSpaceSkinOperator


@dataclass(slots=True, eq=False, repr=False)
class hclObjectSpaceSkinPNTOperator(hclObjectSpaceSkinOperator):
    alignment = 8
    byte_size = 296
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3245113506
    __version = 1

    local_members = (
        Member(264, "localPNTs", hkArray(hclObjectSpaceDeformerLocalBlockPNT, hsh=3862559966)),
        Member(280, "localUnpackedPNTs", hkArray(hclObjectSpaceDeformerLocalBlockUnpackedPNT)),
    )
    members = hclObjectSpaceSkinOperator.members + local_members

    localPNTs: list[hclObjectSpaceDeformerLocalBlockPNT]
    localUnpackedPNTs: list[hclObjectSpaceDeformerLocalBlockUnpackedPNT]
