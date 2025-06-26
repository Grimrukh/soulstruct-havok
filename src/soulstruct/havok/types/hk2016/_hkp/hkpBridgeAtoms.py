from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkpBridgeConstraintAtom import hkpBridgeConstraintAtom


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpBridgeAtoms(hk):
    alignment = 16
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "bridgeAtom", hkpBridgeConstraintAtom),
    )
    members = local_members

    bridgeAtom: hkpBridgeConstraintAtom
