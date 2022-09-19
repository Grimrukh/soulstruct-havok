from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *




from .hclShape import hclShape






class hclCollidable(hkReferencedObject):
    alignment = 16
    byte_size = 160
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 4288064896
    __version = 4

    local_members = (
        Member(32, "transform", hkTransform),
        Member(96, "linearVelocity", hkVector4),
        Member(112, "angularVelocity", hkVector4),
        Member(128, "userData", hkUint64),
        Member(136, "shape", Ptr(hclShape, hsh=849809137)),
        Member(144, "name", hkStringPtr),
        Member(152, "pinchDetectionRadius", hkReal),
        Member(156, "pinchDetectionPriority", hkInt8),
        Member(157, "pinchDetectionEnabled", hkBool),
        Member(158, "virtualCollisionPointCollisionEnabled", hkBool),
        Member(159, "enabled", hkBool),
    )
    members = hkReferencedObject.members + local_members

    transform: hkTransform
    linearVelocity: Vector4
    angularVelocity: Vector4
    userData: int
    shape: hclShape
    name: hkStringPtr
    pinchDetectionRadius: float
    pinchDetectionPriority: int
    pinchDetectionEnabled: bool
    virtualCollisionPointCollisionEnabled: bool
    enabled: bool
