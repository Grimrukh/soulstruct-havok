from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


from .hkaiUserEdgeUtilsUserEdgeSetup import hkaiUserEdgeUtilsUserEdgeSetup


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaiUserEdgeSetupArray(hkReferencedObject):
    alignment = 8
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2665398879

    local_members = (
        Member(24, "edgeSetups", hkArray(hkaiUserEdgeUtilsUserEdgeSetup, hsh=2296997616)),
    )
    members = hkReferencedObject.members + local_members

    edgeSetups: list[hkaiUserEdgeUtilsUserEdgeSetup]
