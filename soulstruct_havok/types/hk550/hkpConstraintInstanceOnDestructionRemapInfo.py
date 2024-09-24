from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpConstraintInstanceOnDestructionRemapInfo(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.Int8
    __real_name = "hkpConstraintInstance::OnDestructionRemapInfo"
    local_members = ()