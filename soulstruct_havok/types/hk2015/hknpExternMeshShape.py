from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


from .hknpCompositeShape import hknpCompositeShape
from .hknpExternMeshShapeGeometry import hknpExternMeshShapeGeometry


class hknpExternMeshShape(hknpCompositeShape):
    alignment = 16
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member(64, "geometry", Ptr(hknpExternMeshShapeGeometry), MemberFlags.Protected),
        Member(68, "boundingVolumeData", Ptr(hkReferencedObject), MemberFlags.Protected),
    )
    members = hknpCompositeShape.members + local_members

    geometry: hknpExternMeshShapeGeometry
    boundingVolumeData: hkReferencedObject