from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpDragProperties(hk):
    alignment = 16
    byte_size = 192
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "centerAndOffset", hkGenericStruct(hkVector4, 3)),
        Member(48, "angularEffectsAndArea", hkGenericStruct(hkVector4, 6)),
        Member(144, "armUVs", hkGenericStruct(hkReal, 12)),
    )
    members = local_members

    centerAndOffset: tuple[hkVector4]
    angularEffectsAndArea: tuple[hkVector4]
    armUVs: tuple[hkReal]
