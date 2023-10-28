from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkp3dAngConstraintAtom(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "padding", hkStruct(hkUint8, 14), extra_flags=MemberFlags.NotSerializable),
    )
    members = local_members

    padding: tuple[int, ...]
