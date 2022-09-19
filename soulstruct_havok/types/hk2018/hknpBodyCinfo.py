from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hknpShape import hknpShape











from .hknpRefMassDistribution import hknpRefMassDistribution
from .hknpRefDragProperties import hknpRefDragProperties
from .hknpBodyId import hknpBodyId

from .hkLocalFrame import hkLocalFrame



class hknpBodyCinfo(hk):
    alignment = 16
    byte_size = 176
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 8

    local_members = (
        Member(0, "shape", hkRefPtr(hknpShape, hsh=1605499205)),
        Member(8, "flags", _int),
        Member(12, "collisionCntrl", _short),
        Member(16, "collisionFilterInfo", hkUint32),
        Member(20, "materialId", _unsigned_short),
        Member(22, "qualityId", _unsigned_char),
        Member(24, "name", hkStringPtr),
        Member(32, "userData", hkUint64),
        Member(40, "motionType", _unsigned_char),
        Member(48, "position", hkVector4),
        Member(64, "orientation", hkQuaternion),
        Member(80, "linearVelocity", hkVector4),
        Member(96, "angularVelocity", hkVector4),
        Member(112, "mass", hkReal),
        Member(120, "massDistribution", hkRefPtr(hknpRefMassDistribution)),
        Member(128, "dragProperties", hkRefPtr(hknpRefDragProperties, hsh=1688167918)),
        Member(136, "motionPropertiesId", _unsigned_short),
        Member(140, "desiredBodyId", hknpBodyId),
        Member(144, "motionId", _unsigned_int),
        Member(148, "collisionLookAheadDistance", hkReal),
        Member(152, "localFrame", hkRefPtr(hkLocalFrame)),
        Member(160, "activationPriority", hkInt8),
    )
    members = local_members

    shape: hknpShape
    flags: int
    collisionCntrl: int
    collisionFilterInfo: int
    materialId: int
    qualityId: int
    name: hkStringPtr
    userData: int
    motionType: int
    position: Vector4
    orientation: hkQuaternion
    linearVelocity: Vector4
    angularVelocity: Vector4
    mass: float
    massDistribution: hknpRefMassDistribution
    dragProperties: hknpRefDragProperties
    motionPropertiesId: int
    desiredBodyId: hknpBodyId
    motionId: int
    collisionLookAheadDistance: float
    localFrame: hkLocalFrame
    activationPriority: int
