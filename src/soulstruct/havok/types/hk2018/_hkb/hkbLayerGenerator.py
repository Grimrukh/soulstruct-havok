from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkbGenerator import hkbGenerator
from .hkbLayer import hkbLayer


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbLayerGenerator(hkbGenerator):
    alignment = 8
    byte_size = 200
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2132817841

    local_members = (
        Member(152, "layers", hkArray(Ptr(hkbLayer, hsh=628661778), hsh=4110935537)),
        Member(168, "indexOfSyncMasterChild", hkInt16),
        Member(170, "flags", hkFlags(hkUint16)),
        Member(172, "numActiveLayers", _int, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(
            176,
            "layerInternalStates",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(192, "initSync", hkBool, MemberFlags.NotSerializable | MemberFlags.Private),
    )
    members = hkbGenerator.members + local_members

    layers: list[hkbLayer]
    indexOfSyncMasterChild: int
    flags: hkUint16
    numActiveLayers: int
    layerInternalStates: list[hkReflectDetailOpaque]
    initSync: bool
