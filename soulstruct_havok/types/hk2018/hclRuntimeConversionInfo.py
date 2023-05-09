from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hclRuntimeConversionInfoSlotConversion import hclRuntimeConversionInfoSlotConversion
from .hclRuntimeConversionInfoElementConversion import hclRuntimeConversionInfoElementConversion


@dataclass(slots=True, eq=False, repr=False)
class hclRuntimeConversionInfo(hk):
    alignment = 1
    byte_size = 42
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 0

    local_members = (
        Member(0, "slotConversions", hkGenericStruct(hclRuntimeConversionInfoSlotConversion, 4)),
        Member(28, "elementConversions", hkGenericStruct(hclRuntimeConversionInfoElementConversion, 4)),
        Member(40, "numSlotsConverted", hkUint8),
        Member(41, "numElementsConverted", hkUint8),
    )
    members = local_members

    slotConversions: tuple[hclRuntimeConversionInfoSlotConversion]
    elementConversions: tuple[hclRuntimeConversionInfoElementConversion]
    numSlotsConverted: int
    numElementsConverted: int
