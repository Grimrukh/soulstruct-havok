from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hknpSparseCompactMap(hk):
    alignment = 4
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "secondaryKeyMask", hkUint32),
        Member(4, "sencondaryKeyBits", hkUint32),
        Member(8, "primaryKeyToIndex", hkArray(hkUint16)),
        Member(20, "valueAndSecondaryKeys", hkArray(hkUint16)),
    )
    members = local_members

    secondaryKeyMask: int
    sencondaryKeyBits: int
    primaryKeyToIndex: list[int]
    valueAndSecondaryKeys: list[int]

    __templates = (
        TemplateType("tStoreT", type=hkUint16),
    )
