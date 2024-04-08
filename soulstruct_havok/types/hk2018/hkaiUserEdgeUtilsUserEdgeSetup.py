from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkaiUserEdgeUtilsObb import hkaiUserEdgeUtilsObb
from .hkaiUserEdgeUtilsUserEdgeDirection import hkaiUserEdgeUtilsUserEdgeDirection
from .hkaiUserEdgeUtilsUserEdgeSetupSpace import hkaiUserEdgeUtilsUserEdgeSetupSpace


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaiUserEdgeUtilsUserEdgeSetup(hk):
    alignment = 16
    byte_size = 224
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 1635166183
    __version = 2
    __real_name = "hkaiUserEdgeUtils::UserEdgeSetup"

    local_members = (
        Member(0, "obbA", hkaiUserEdgeUtilsObb),
        Member(80, "obbB", hkaiUserEdgeUtilsObb),
        Member(160, "userDataA", hkUint32),
        Member(164, "userDataB", hkUint32),
        Member(168, "costAtoB", hkReal),
        Member(172, "costBtoA", hkReal),
        Member(176, "worldUpA", hkVector4),
        Member(192, "worldUpB", hkVector4),
        Member(208, "direction", hkEnum(hkaiUserEdgeUtilsUserEdgeDirection, hkUint8)),
        Member(209, "space", hkEnum(hkaiUserEdgeUtilsUserEdgeSetupSpace, hkUint8)),
        Member(210, "forceAlign", hkBool),
    )
    members = local_members

    obbA: hkaiUserEdgeUtilsObb
    obbB: hkaiUserEdgeUtilsObb
    userDataA: int
    userDataB: int
    costAtoB: float
    costBtoA: float
    worldUpA: hkVector4
    worldUpB: hkVector4
    direction: hkaiUserEdgeUtilsUserEdgeDirection
    space: hkaiUserEdgeUtilsUserEdgeSetupSpace
    forceAlign: bool
