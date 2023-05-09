from __future__ import annotations

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
    byte_size = 704
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 5

    local_members = (
        Member(200, "material", hkpMaterial, MemberFlags.Protected),
        Member(216, "limitContactImpulseUtilAndFlag", Ptr(_void), MemberFlags.NotSerializable),
        Member(224, "damageMultiplier", hkReal),
        Member(232, "breakableBody", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(240, "solverData", hkUint32, MemberFlags.NotSerializable),
        Member(244, "storageIndex", _unsigned_short),
        Member(246, "contactPointCallbackDelay", hkUint16, MemberFlags.Protected),
        Member(
            248,
            "constraintsMaster",
            hkpEntitySmallArraySerializeOverrideType,
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(
            264,
            "constraintsSlave",
            hkArray(hkViewPtr("hkpConstraintInstance", hsh=3107152142)),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(
            280,
            "constraintRuntime",
            hkArray(hkUint8, hsh=2877151166),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(
            296,
            "simulationIsland",
            Ptr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(304, "autoRemoveLevel", hkInt8),
        Member(305, "numShapeKeysInContactPointProperties", hkUint8),
        Member(306, "responseModifierFlags", hkUint8),
        Member(308, "uid", hkUint32),
        Member(312, "spuCollisionCallback", hkpEntitySpuCollisionCallback),
        Member(336, "motion", hkpMaxSizeMotion),
        Member(
            656,
            "contactListeners",
            hkpEntitySmallArraySerializeOverrideType,
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(
            672,
            "actions",
            hkpEntitySmallArraySerializeOverrideType,
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(688, "localFrame", hkRefPtr(hkLocalFrame)),
        Member(
            696,
            "extendedListeners",
            Ptr(hkpEntityExtendedListeners),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
    )
    members = hkpWorldObject.members + local_members

    material: hkpMaterial
    limitContactImpulseUtilAndFlag: _void
    damageMultiplier: float
    breakableBody: hkReflectDetailOpaque
    solverData: int
    storageIndex: int
    contactPointCallbackDelay: int
    constraintsMaster: hkpEntitySmallArraySerializeOverrideType
    constraintsSlave: list[hkpConstraintInstance]
    constraintRuntime: list[int]
    simulationIsland: hkReflectDetailOpaque
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
