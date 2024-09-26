from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkpConstraintData import hkpConstraintData


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpConstraintChainData(hkpConstraintData):
    alignment = 8
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 3
    local_members = ()
