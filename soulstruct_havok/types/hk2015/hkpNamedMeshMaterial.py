from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkpMeshMaterial import hkpMeshMaterial


@dataclass(slots=True, eq=False, repr=False)
class hkpNamedMeshMaterial(hkpMeshMaterial):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "name", hkStringPtr),
    )
    members = hkpMeshMaterial.members + local_members

    name: str
