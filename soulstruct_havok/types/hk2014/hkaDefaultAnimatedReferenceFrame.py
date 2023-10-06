from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkaAnimatedReferenceFrame import hkaAnimatedReferenceFrame


@dataclass(slots=True, eq=False, repr=False)
class hkaDefaultAnimatedReferenceFrame(hkaAnimatedReferenceFrame):
    alignment = 16
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2816999057

    local_members = (
        Member(32, "up", hkVector4),
        Member(48, "forward", hkVector4),
        Member(64, "duration", hkReal),
        Member(72, "referenceFrameSamples", hkArray(hkVector4, hsh=2234779563)),
    )
    members = hkaAnimatedReferenceFrame.members + local_members

    up: Vector4
    forward: Vector4
    duration: float
    referenceFrameSamples: list[hkVector4]