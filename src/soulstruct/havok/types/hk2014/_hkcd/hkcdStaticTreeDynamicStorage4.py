from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *

from .hkcdStaticTreeDynamicStoragehkcdStaticTreeCodec3Axis4 import hkcdStaticTreeDynamicStoragehkcdStaticTreeCodec3Axis4


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkcdStaticTreeDynamicStorage4(hkcdStaticTreeDynamicStoragehkcdStaticTreeCodec3Axis4):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1556242320

    local_members = ()
