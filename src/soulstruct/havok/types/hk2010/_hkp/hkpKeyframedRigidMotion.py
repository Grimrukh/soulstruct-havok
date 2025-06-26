from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkpMotion import hkpMotion


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpKeyframedRigidMotion(hkpMotion):
    alignment = 16
    byte_size = 288
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    local_members = ()
