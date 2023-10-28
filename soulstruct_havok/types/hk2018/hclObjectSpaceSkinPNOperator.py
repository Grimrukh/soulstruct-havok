from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hclObjectSpaceDeformerLocalBlockPN import hclObjectSpaceDeformerLocalBlockPN
from .hclObjectSpaceDeformerLocalBlockUnpackedPN import hclObjectSpaceDeformerLocalBlockUnpackedPN
from .hclObjectSpaceSkinOperator import hclObjectSpaceSkinOperator


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclObjectSpaceSkinPNOperator(hclObjectSpaceSkinOperator):
    alignment = 8
    byte_size = 296
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3646506320
    __version = 1

    local_members = (
        Member(264, "localPNs", hkArray(hclObjectSpaceDeformerLocalBlockPN, hsh=4080327730)),
        Member(280, "localUnpackedPNs", hkArray(hclObjectSpaceDeformerLocalBlockUnpackedPN)),
    )
    members = hclObjectSpaceSkinOperator.members + local_members

    localPNs: list[hclObjectSpaceDeformerLocalBlockPN]
    localUnpackedPNs: list[hclObjectSpaceDeformerLocalBlockUnpackedPN]
