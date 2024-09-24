from __future__ import annotations

import typing as tp
from dataclasses import dataclass, field

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


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpEntity(hkpWorldObject):
    alignment = 16
    byte_size = 512  # Havok tried to keep this class under 512 bytes (obviously failed in new versions)
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(128, "material", hkpMaterial),  # 12
        Member(140, "breakOffPartsUtil", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(144, "solverData", hkUint32, MemberFlags.NotSerializable),
        Member(148, "storageIndex", hkUint16),
        Member(150, "contactPointCallbackDelay", hkUint16),
        Member(152, "constraintsMaster", hkpEntitySmallArraySerializeOverrideType, MemberFlags.NotSerializable),
        Member(
            160,
            "constraintsSlave",
            hkArray(Ptr(hkViewPtr("hkpConstraintInstance"))),
            MemberFlags.NotSerializable,
        ),
        Member(172, "constraintRuntime", hkArray(hkUint8), MemberFlags.NotSerializable),
        Member(184, "simulationIsland", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(188, "autoRemoveLevel", hkInt8),
        Member(189, "numUserDatasInContactPointProperties", hkUint8),
        Member(192, "uid", hkUint32),
        Member(196, "spuCollisionCallback", hkpEntitySpuCollisionCallback),  # 8
        Member(204, "extendedListeners", Ptr(hkpEntityExtendedListeners), MemberFlags.NotSerializable),
        Member(208, "motion", hkpMaxSizeMotion),  # 288
        Member(496, "collisionListeners", hkpEntitySmallArraySerializeOverrideType, MemberFlags.NotSerializable),
        Member(504, "actions", hkpEntitySmallArraySerializeOverrideType, MemberFlags.NotSerializable),
    )
    members = hkpWorldObject.members + local_members

    material: hkpMaterial
    breakOffPartsUtil: None = None
    solverData: int = 0
    storageIndex: int
    contactPointCallbackDelay: int
    constraintsMaster: hkpEntitySmallArraySerializeOverrideType = None
    constraintsSlave: list[hkpConstraintInstance] = field(default_factory=list)
    constraintRuntime: list[int] = field(default_factory=list)
    simulationIsland: None = None
    autoRemoveLevel: int
    numUserDatasInContactPointProperties: int
    uid: int
    spuCollisionCallback: hkpEntitySpuCollisionCallback
    extendedListeners: hkpEntityExtendedListeners = None
    motion: hkpMaxSizeMotion
    collisionListeners: hkpEntitySmallArraySerializeOverrideType = None
    actions: hkpEntitySmallArraySerializeOverrideType = None
