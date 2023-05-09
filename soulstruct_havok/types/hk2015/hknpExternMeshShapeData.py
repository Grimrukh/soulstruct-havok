from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


from .hkcdStaticTreeTree import hkcdStaticTreeTree
from .hkcdSimdTree import hkcdSimdTree


@dataclass(slots=True, eq=False, repr=False)
class hknpExternMeshShapeData(hkReferencedObject):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(0, "aabbTree", hkcdStaticTreeTree),
        Member(48, "simdTree", hkcdSimdTree),
        Member(60, "hasBuildContext", hkBool),
    )
    members = hkReferencedObject.members + local_members

    aabbTree: hkcdStaticTreeTree
    simdTree: hkcdSimdTree
    hasBuildContext: bool
