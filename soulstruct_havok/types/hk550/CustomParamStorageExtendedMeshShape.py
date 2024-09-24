from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .CustomMeshParameter import CustomMeshParameter
from .hkpStorageExtendedMeshShape import hkpStorageExtendedMeshShape


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class CustomParamStorageExtendedMeshShape(hkpStorageExtendedMeshShape):
    alignment = 16
    byte_size = 240
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(
            216,
            "materialArray",
            hkArray(Ptr(CustomMeshParameter)),
            MemberFlags.Private,
        ),
    )
    members = hkpStorageExtendedMeshShape.members + local_members

    materialArray: list[CustomMeshParameter]
