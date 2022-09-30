from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hclOperator import hclOperator

from .hclRuntimeConversionInfo import hclRuntimeConversionInfo


class hclOutputConvertOperator(hclOperator):
    alignment = 8
    byte_size = 128
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3763320081

    local_members = (
        Member(72, "userBufferIndex", hkUint32),
        Member(76, "shadowBufferIndex", hkUint32),
        Member(80, "conversionInfo", hclRuntimeConversionInfo),
    )
    members = hclOperator.members + local_members

    userBufferIndex: int
    shadowBufferIndex: int
    conversionInfo: hclRuntimeConversionInfo