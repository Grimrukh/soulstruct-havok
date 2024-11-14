from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxCamera(hk):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3586547630

    local_members = (
        Member(0, "from_", hkVector4),
        Member(16, "focus", hkVector4),
        Member(32, "up", hkVector4),
        Member(48, "fov", hkReal),
        Member(52, "far", hkReal),
        Member(56, "near", hkReal),
        Member(60, "leftHanded", hkBool),
    )
    members = local_members

    from_: Vector4  # Python built-in clash
    focus: Vector4
    up: Vector4
    fov: float
    far: float
    near: float
    leftHanded: bool
