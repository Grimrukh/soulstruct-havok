from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hclOperator import hclOperator



from .hclObjectSpaceDeformer import hclObjectSpaceDeformer


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclObjectSpaceSkinOperator(hclOperator):
    alignment = 8
    byte_size = 264
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 61
    __abstract_value = 3
    __version = 1

    local_members = (
        Member(72, "boneFromSkinMeshTransforms", hkArray(hkMatrix4, hsh=3899186074)),
        Member(88, "transformSubset", hkArray(hkUint16, hsh=3431155310)),
        Member(104, "outputBufferIndex", hkUint32),
        Member(108, "transformSetIndex", hkUint32),
        Member(112, "objectSpaceDeformer", hclObjectSpaceDeformer),
    )
    members = hclOperator.members + local_members

    boneFromSkinMeshTransforms: list[hkMatrix4]
    transformSubset: list[int]
    outputBufferIndex: int
    transformSetIndex: int
    objectSpaceDeformer: hclObjectSpaceDeformer
