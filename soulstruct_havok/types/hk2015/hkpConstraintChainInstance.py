from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


from .hkpConstraintInstance import hkpConstraintInstance
from .hkpEntity import hkpEntity
from .hkpConstraintChainInstanceAction import hkpConstraintChainInstanceAction


@dataclass(slots=True, eq=False, repr=False)
class hkpConstraintChainInstance(hkpConstraintInstance):
    alignment = 8
    byte_size = 144
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3870812330
    __version = 1

    local_members = (
        Member(112, "chainedEntities", hkArray(Ptr(hkpEntity, hsh=476716456), hsh=325243755)),
        Member(128, "action", Ptr(hkpConstraintChainInstanceAction, hsh=2500488554)),
        Member(136, "chainConnectedness", hkUlong),
    )
    members = hkpConstraintInstance.members + local_members

    chainedEntities: list[hkpEntity]
    action: hkpConstraintChainInstanceAction
    chainConnectedness: int
