from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkpKeyframedRigidMotion import hkpKeyframedRigidMotion


@dataclass(slots=True, eq=False, repr=False)
class hkpMaxSizeMotion(hkpKeyframedRigidMotion):
    alignment = 16
    byte_size = 288
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    local_members = ()
