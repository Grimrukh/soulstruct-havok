from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *

from .hkpShape import hkpShape
from .hkpBvTreeShapeBvTreeType import hkpBvTreeShapeBvTreeType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpBvTreeShape(hkpShape):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 61

    # No members.
