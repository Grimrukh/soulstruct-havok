from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkbGenerator import hkbGenerator


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbReferencePoseGenerator(hkbGenerator):
    alignment = 8
    byte_size = 160
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3633547704

    local_members = (
        Member(152, "skeleton", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable | MemberFlags.Private),
    )
    members = hkbGenerator.members + local_members

    skeleton: hkReflectDetailOpaque
