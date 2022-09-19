from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *

from .hclRuntimeConversionInfoVectorConversion import hclRuntimeConversionInfoVectorConversion


class hclRuntimeConversionInfoElementConversion(hk):
    alignment = 1
    byte_size = 3
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hclRuntimeConversionInfo::ElementConversion"

    local_members = (
        Member(0, "index", hkUint8),
        Member(1, "offset", hkUint8),
        Member(2, "conversion", hkEnum(hclRuntimeConversionInfoVectorConversion, hkUint8)),
    )
    members = local_members

    index: int
    offset: int
    conversion: hclRuntimeConversionInfoVectorConversion
