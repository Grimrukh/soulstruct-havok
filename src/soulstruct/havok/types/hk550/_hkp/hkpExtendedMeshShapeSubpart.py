from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkpExtendedMeshShapeMaterialIndexStridingType import hkpExtendedMeshShapeMaterialIndexStridingType
from .hkpExtendedMeshShapeSubpartType import hkpExtendedMeshShapeSubpartType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpExtendedMeshShapeSubpart(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __real_name = "hkpExtendedMeshShape::Subpart"

    local_members = (
        Member(0, "type", hkEnum(hkpExtendedMeshShapeSubpartType, hkUint8)),  # indicates subclass
        Member(1, "materialIndexStridingType", hkEnum(hkpExtendedMeshShapeMaterialIndexStridingType, hkUint8)),
        Member(2, "materialStriding", hkInt16, MemberFlags.NotSerializable),
        Member(4, "materialIndexBase", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(8, "materialIndexStriding", hkUint16),
        Member(10, "numMaterials", hkUint16),
        Member(12, "materialBase", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
    )
    members = local_members

    type: int
    materialIndexStridingType: int
    materialStriding: int
    materialIndexBase: None = None
    materialIndexStriding: int
    numMaterials: int
    materialBase: None = None
