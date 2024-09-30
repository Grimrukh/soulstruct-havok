from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .._hkcd.hkcdSimdTree import hkcdSimdTree
from .hknpCompressedMeshShapeTree import hknpCompressedMeshShapeTree


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpCompressedMeshShapeData(hkReferencedObject):
    alignment = 16
    byte_size = 208
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2730359897

    local_members = (
        Member(16, "meshTree", hknpCompressedMeshShapeTree),
        Member(176, "simdTree", hkcdSimdTree),
        Member(200, "unk", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),  # TODO: get name from SDK?
    )
    members = hkReferencedObject.members + local_members

    meshTree: hknpCompressedMeshShapeTree
    simdTree: hkcdSimdTree
    unk: None = None
