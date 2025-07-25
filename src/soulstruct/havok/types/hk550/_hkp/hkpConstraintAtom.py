from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkpConstraintAtomAtomType import hkpConstraintAtomAtomType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpConstraintAtom(hk):
    alignment = 2
    byte_size = 2
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "type", hkEnum(hkpConstraintAtomAtomType, hkUint16)),
    )
    members = local_members

    type: int
