from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkcdCompressedAabbCodecsAabbCodecBase import hkcdCompressedAabbCodecsAabbCodecBase


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkcdCompressedAabbCodecsCompressedAabbCodec(hkcdCompressedAabbCodecsAabbCodecBase):
    alignment = 1
    byte_size = 3
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkcdCompressedAabbCodecs::CompressedAabbCodec"

    local_members = (
        Member(0, "xyz", hkGenericStruct(hkUint8, 3)),
    )
    members = hkcdCompressedAabbCodecsAabbCodecBase.members + local_members

    xyz: tuple[hkUint8]
