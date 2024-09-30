from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpSparseCompactMap(hk):
    alignment = 4
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "secondaryKeyMask", hkUint32),
        Member(4, "sencondaryKeyBits", hkUint32),  # Typo in original Havok source.
        Member(8, "primaryKeyToIndex", hkArray(hkUint16)),
        Member(24, "valueAndSecondaryKeys", hkArray(hkUint16)),
    )
    members = local_members

    secondaryKeyMask: int
    sencondaryKeyBits: int
    primaryKeyToIndex: list[int]
    valueAndSecondaryKeys: list[int]

    __templates = (
        TemplateType("tStoreT", _type=hkUint16),
    )