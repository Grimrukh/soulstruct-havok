from __future__ import annotations

import typing as tp

from soulstruct_havok.enums import *
from soulstruct_havok.types.core import *
from .hkpAction import hkpAction

if tp.TYPE_CHECKING:
    from .hkpConstraintChainInstance import hkpConstraintChainInstance


class hkpConstraintChainInstanceAction(hkpAction):
    alignment = 8
    byte_size = 56
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2211512732

    local_members = (
        Member(48, "constraintInstance", hkViewPtr("hkpConstraintChainInstance")),
    )
    members = hkpAction.members + local_members

    constraintInstance: hkpConstraintChainInstance
