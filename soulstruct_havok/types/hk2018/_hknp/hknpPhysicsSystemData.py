from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *

from .hknpMaterial import hknpMaterial
from .hknpMotionProperties import hknpMotionProperties
from .hknpPhysicsSystemDatabodyCinfoWithAttachment import hknpPhysicsSystemDatabodyCinfoWithAttachment
from .hknpConstraintCinfo import hknpConstraintCinfo


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpPhysicsSystemData(hkReferencedObject):
    alignment = 8
    byte_size = 104
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 3

    local_members = (
        Member(24, "materials", hkArray(hknpMaterial, hsh=881367723)),
        Member(40, "motionProperties", hkArray(hknpMotionProperties, hsh=2250204073)),
        Member(56, "bodyCinfos", hkArray(hknpPhysicsSystemDatabodyCinfoWithAttachment, hsh=2094859555)),
        Member(72, "constraintCinfos", hkArray(hknpConstraintCinfo, hsh=2195283511)),
        Member(88, "name", hkStringPtr),
        Member(96, "microStepMultiplier", hkUint8),
    )
    members = hkReferencedObject.members + local_members

    materials: list[hknpMaterial]
    motionProperties: list[hknpMotionProperties]
    bodyCinfos: list[hknpPhysicsSystemDatabodyCinfoWithAttachment]
    constraintCinfos: list[hknpConstraintCinfo]
    name: hkStringPtr
    microStepMultiplier: int
