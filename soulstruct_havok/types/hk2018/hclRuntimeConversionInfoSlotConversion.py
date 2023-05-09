from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hclRuntimeConversionInfoSlotConversion(hk):
    alignment = 1
    byte_size = 7
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hclRuntimeConversionInfo::SlotConversion"

    local_members = (
        Member(0, "elements", hkGenericStruct(hkUint8, 4)),
        Member(4, "numElements", hkUint8),
        Member(5, "index", hkUint8),
        Member(6, "partialWrite", hkBool),
    )
    members = local_members

    elements: tuple[hkUint8]
    numElements: int
    index: int
    partialWrite: bool
