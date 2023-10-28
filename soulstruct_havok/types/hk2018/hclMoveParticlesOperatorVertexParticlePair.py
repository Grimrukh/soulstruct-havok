from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclMoveParticlesOperatorVertexParticlePair(hk):
    alignment = 2
    byte_size = 4
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3905957961
    __real_name = "hclMoveParticlesOperator::VertexParticlePair"

    local_members = (
        Member(0, "vertexIndex", hkUint16),
        Member(2, "particleIndex", hkUint16),
    )
    members = local_members

    vertexIndex: int
    particleIndex: int
