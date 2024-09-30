from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .CustomMeshParameter import CustomMeshParameter
from ._hkp.hkpStorageExtendedMeshShape import hkpStorageExtendedMeshShape


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class CustomParamStorageExtendedMeshShape(hkpStorageExtendedMeshShape):
    alignment = 16
    byte_size = 368
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2448234539

    local_members = (
        Member(
            352,
            "materialArray",
            hkArray(Ptr(CustomMeshParameter, hsh=927471100), hsh=1999126890),
            MemberFlags.Private,
        ),
    )
    members = hkpStorageExtendedMeshShape.members + local_members

    materialArray: list[CustomMeshParameter]
