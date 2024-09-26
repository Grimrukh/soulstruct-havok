from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from ..hkAabb import hkAabb
from .hkcdStaticTreeDynamicStorage5 import hkcdStaticTreeDynamicStorage5


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkcdStaticTreeTreehkcdStaticTreeDynamicStorage5(hkcdStaticTreeDynamicStorage5):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 486420406

    local_members = (
        Member(16, "domain", hkAabb),
    )
    members = hkcdStaticTreeDynamicStorage5.members + local_members

    domain: hkAabb
