from __future__ import annotations

from soulstruct_havok.enums import *
from soulstruct_havok.types.core import *
from .hkpBridgeConstraintAtom import hkpBridgeConstraintAtom


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
