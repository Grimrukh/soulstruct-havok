from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *

from .hknpMassDistribution import hknpMassDistribution


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpRefMassDistribution(hkReferencedObject):
    alignment = 16
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(32, "massDistribution", hknpMassDistribution),
    )
    members = hkReferencedObject.members + local_members

    massDistribution: hknpMassDistribution
