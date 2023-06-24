from __future__ import annotations

from dataclasses import dataclass



import typing as tp

from soulstruct_havok.enums import *
from .core import *
from .hkpWorldObject import hkpWorldObject
from .hkpMaterial import hkpMaterial
from .hkpEntitySmallArraySerializeOverrideType import hkpEntitySmallArraySerializeOverrideType
from .hkpEntitySpuCollisionCallback import hkpEntitySpuCollisionCallback
from .hkpMaxSizeMotion import hkpMaxSizeMotion
from .hkLocalFrame import hkLocalFrame
from .hkpEntityExtendedListeners import hkpEntityExtendedListeners

if tp.TYPE_CHECKING:
    from .hkpConstraintInstance import hkpConstraintInstance


@dataclass(slots=True, eq=False, repr=False)
class hkpEntity(hkpWorldObject):
    alignment = 16
    byte_size = 544
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(140, "material", hkpMaterial),
        Member(152, "limitContactImpulseUtilAndFlag", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(156, "damageMultiplier", hkReal),
        Member(160, "breakableBody", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(164, "solverData", hkUint32, MemberFlags.NotSerializable),
        Member(168, "storageIndex", hkUint16),
        Member(170, "contactPointCallbackDelay", hkUint16),
        Member(172, "constraintsMaster", hkpEntitySmallArraySerializeOverrideType, MemberFlags.NotSerializable),
        Member(
            180,
            "constraintsSlave",
            hkArray(Ptr(hkViewPtr("hkpConstraintInstance"))),
            MemberFlags.NotSerializable,
        ),
        Member(192, "constraintRuntime", hkArray(hkUint8), MemberFlags.NotSerializable),
        Member(204, "simulationIsland", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(208, "autoRemoveLevel", hkInt8),
        Member(209, "numShapeKeysInContactPointProperties", hkUint8),
        Member(210, "responseModifierFlags", hkUint8),
        Member(212, "uid", hkUint32),
        Member(216, "spuCollisionCallback", hkpEntitySpuCollisionCallback),
        Member(224, "motion", hkpMaxSizeMotion),
        Member(512, "contactListeners", hkpEntitySmallArraySerializeOverrideType, MemberFlags.NotSerializable),
        Member(520, "actions", hkpEntitySmallArraySerializeOverrideType, MemberFlags.NotSerializable),
        Member(528, "localFrame", Ptr(hkLocalFrame)),
        Member(532, "extendedListeners", Ptr(hkpEntityExtendedListeners), MemberFlags.NotSerializable),
        Member(536, "npData", hkUint32),
    )
    members = hkpWorldObject.members + local_members

    material: hkpMaterial
    limitContactImpulseUtilAndFlag: None
    damageMultiplier: float
    breakableBody: None
    solverData: int
    storageIndex: int
    contactPointCallbackDelay: int
    constraintsMaster: hkpEntitySmallArraySerializeOverrideType
    constraintsSlave: list[hkpConstraintInstance]
    constraintRuntime: list[int]
    simulationIsland: None
    autoRemoveLevel: int
    numShapeKeysInContactPointProperties: int
    responseModifierFlags: int
    uid: int
    spuCollisionCallback: hkpEntitySpuCollisionCallback
    motion: hkpMaxSizeMotion
    contactListeners: hkpEntitySmallArraySerializeOverrideType
    actions: hkpEntitySmallArraySerializeOverrideType
    localFrame: hkLocalFrame
    extendedListeners: hkpEntityExtendedListeners
    npData: int
