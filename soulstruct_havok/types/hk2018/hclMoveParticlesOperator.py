from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hclOperator import hclOperator
from .hclMoveParticlesOperatorVertexParticlePair import hclMoveParticlesOperatorVertexParticlePair


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclMoveParticlesOperator(hclOperator):
    alignment = 8
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3249942978

    local_members = (
        Member(72, "vertexParticlePairs", hkArray(hclMoveParticlesOperatorVertexParticlePair, hsh=2796431132)),
        Member(88, "simClothIndex", hkUint32),
        Member(92, "refBufferIdx", hkUint32),
    )
    members = hclOperator.members + local_members

    vertexParticlePairs: list[hclMoveParticlesOperatorVertexParticlePair]
    simClothIndex: int
    refBufferIdx: int
