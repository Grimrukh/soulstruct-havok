from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *

from .hknpManifoldTypeEnum import hknpManifoldTypeEnum


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpBodyIntegrator(hkReferencedObject):
    alignment = 8
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(20, "bodyFlagsForcingNormalCollisions", _unsigned_int),
        Member(24, "typeForDynamicBodies", hknpManifoldTypeEnum),
        Member(28, "typeForTriggers", hknpManifoldTypeEnum),
    )
    members = hkReferencedObject.members + local_members

    bodyFlagsForcingNormalCollisions: int
    typeForDynamicBodies: int
    typeForTriggers: int
