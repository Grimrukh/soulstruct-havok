from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkpPropertyValue import hkpPropertyValue


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpProperty(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "key", hkUint32),
        Member(4, "alignmentPadding", hkUint32),
        Member(8, "value", hkpPropertyValue),
    )
    members = local_members

    key: int
    alignmentPadding: int
    value: hkpPropertyValue
