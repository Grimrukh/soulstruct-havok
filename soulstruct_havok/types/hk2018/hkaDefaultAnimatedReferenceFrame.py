from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkaAnimatedReferenceFrame import hkaAnimatedReferenceFrame


@dataclass(slots=True, eq=False, repr=False)
class hkaDefaultAnimatedReferenceFrame(hkaAnimatedReferenceFrame):
    alignment = 16
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2865971695

    local_members = (
        Member(32, "up", hkVector4),
        Member(48, "forward", hkVector4),
        Member(64, "duration", hkReal),
        Member(72, "referenceFrameSamples", hkArray(hkVector4, hsh=1398146255)),
    )
    members = hkaAnimatedReferenceFrame.members + local_members

    up: hkVector4
    forward: hkVector4
    duration: float
    referenceFrameSamples: list[hkVector4]
