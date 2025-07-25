from __future__ import annotations

from dataclasses import dataclass

import typing as tp

from soulstruct.havok.enums import *
from ..core import *
from .hkpAction import hkpAction

if tp.TYPE_CHECKING:
    from .hkpConstraintChainInstance import hkpConstraintChainInstance


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
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
