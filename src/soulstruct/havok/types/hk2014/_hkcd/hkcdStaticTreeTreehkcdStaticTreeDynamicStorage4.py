from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from ..hkAabb import hkAabb
from .hkcdStaticTreeDynamicStorage4 import hkcdStaticTreeDynamicStorage4


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkcdStaticTreeTreehkcdStaticTreeDynamicStorage4(hkcdStaticTreeDynamicStorage4):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3859019434

    local_members = (
        Member(16, "domain", hkAabb),
    )
    members = hkcdStaticTreeDynamicStorage4.members + local_members

    domain: hkAabb
