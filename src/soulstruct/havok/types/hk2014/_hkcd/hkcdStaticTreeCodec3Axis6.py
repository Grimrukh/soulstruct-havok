from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *

from .hkcdStaticTreeCodec3Axis import hkcdStaticTreeCodec3Axis


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkcdStaticTreeCodec3Axis6(hkcdStaticTreeCodec3Axis):
    alignment = 2
    byte_size = 6
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkcdStaticTree::Codec3Axis6"
    __hsh = 1453022594

    local_members = (
        Member(3, "hiData", hkUint8),
        Member(4, "loData", hkUint16),
    )
    members = hkcdStaticTreeCodec3Axis.members + local_members

    hiData: int
    loData: int

    # No primitive unpack/pack method, as `loData` is 16-bit.
