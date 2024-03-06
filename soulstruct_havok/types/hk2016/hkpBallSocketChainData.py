from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *

from .hkpConstraintChainData import hkpConstraintChainData
from .hkpBridgeAtoms import hkpBridgeAtoms
from .hkpBallSocketChainDataConstraintInfo import hkpBallSocketChainDataConstraintInfo


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpBallSocketChainData(hkpConstraintChainData):
    alignment = 16
    byte_size = 128
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3612460212
    __version = 2

    local_members = (
        Member(32, "atoms", hkpBridgeAtoms),
        Member(64, "infos", hkArray(hkpBallSocketChainDataConstraintInfo, hsh=3025403522)),
        Member(80, "link0PivotBVelocity", hkVector4),
        Member(96, "tau", hkReal),
        Member(100, "damping", hkReal),
        Member(104, "cfm", hkReal),
        Member(108, "maxErrorDistance", hkReal),
        Member(112, "inertiaPerMeter", hkReal),
        Member(116, "useStabilizedCode", _bool, MemberFlags.Private),
    )
    members = hkpConstraintChainData.members + local_members

    atoms: hkpBridgeAtoms
    infos: list[hkpBallSocketChainDataConstraintInfo]
    link0PivotBVelocity: hkVector4
    tau: float
    damping: float
    cfm: float
    maxErrorDistance: float
    inertiaPerMeter: float
    useStabilizedCode: bool
