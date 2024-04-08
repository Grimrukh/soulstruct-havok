from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkcdCompressedAabbCodecsCompressedAabbCodec import hkcdCompressedAabbCodecsCompressedAabbCodec


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkcdCompressedAabbCodecsAabb6BytesCodec(hkcdCompressedAabbCodecsCompressedAabbCodec):
    alignment = 2
    byte_size = 6
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 531426391
    __real_name = "hkcdCompressedAabbCodecs::Aabb6BytesCodec"

    local_members = (
        Member(3, "hiData", hkUint8),
        Member(4, "loData", hkUint16),
    )
    members = hkcdCompressedAabbCodecsCompressedAabbCodec.members + local_members

    hiData: int
    loData: int
