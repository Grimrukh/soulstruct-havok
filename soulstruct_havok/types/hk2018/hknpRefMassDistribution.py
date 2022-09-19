from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *

from .hknpMassDistribution import hknpMassDistribution


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
