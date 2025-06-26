from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hknpMaterial import hknpMaterial
from .hknpMotionProperties import hknpMotionProperties
from .hknpMotionCinfo import hknpMotionCinfo
from .hknpBodyCinfo import hknpBodyCinfo
from .hknpConstraintCinfo import hknpConstraintCinfo


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpPhysicsSystemData(hkReferencedObject):
    alignment = 16
    byte_size = 120
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "materials", hkArray(hknpMaterial)),
        Member(32, "motionProperties", hkArray(hknpMotionProperties)),
        Member(48, "motionCinfos", hkArray(hknpMotionCinfo)),
        Member(64, "bodyCinfos", hkArray(hknpBodyCinfo)),
        Member(80, "constraintCinfos", hkArray(hknpConstraintCinfo)),
        Member(96, "referencedObjects", hkArray(Ptr(hkReferencedObject))),
        Member(112, "name", hkStringPtr),
    )
    members = hkReferencedObject.members + local_members

    materials: list[hknpMaterial]
    motionProperties: list[hknpMotionProperties]
    motionCinfos: list[hknpMotionCinfo]
    bodyCinfos: list[hknpBodyCinfo]
    constraintCinfos: list[hknpConstraintCinfo]
    referencedObjects: list[hkReferencedObject]
    name: str
