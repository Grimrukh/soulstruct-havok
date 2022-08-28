from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hkpConstraintData import hkpConstraintData
from .hkpModifierConstraintAtom import hkpModifierConstraintAtom
from .hkpEntity import hkpEntity
from .hkpConstraintInstanceConstraintPriority import hkpConstraintInstanceConstraintPriority
from .hkpConstraintInstanceOnDestructionRemapInfo import hkpConstraintInstanceOnDestructionRemapInfo
from .hkpConstraintInstanceSmallArraySerializeOverrideType import hkpConstraintInstanceSmallArraySerializeOverrideType


class hkpConstraintInstance(hkReferencedObject):
    alignment = 8
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(16, "owner", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(24, "data", Ptr(hkpConstraintData, hsh=525862446), MemberFlags.Protected),
        Member(32, "constraintModifiers", Ptr(hkpModifierConstraintAtom), MemberFlags.Protected),
        Member(40, "entities", hkGenericStruct(Ptr(hkpEntity, hsh=476716456), 2), MemberFlags.Protected),
        Member(56, "priority", hkEnum(hkpConstraintInstanceConstraintPriority, hkUint8)),
        Member(57, "wantRuntime", hkBool, MemberFlags.Protected),
        Member(58, "destructionRemapInfo", hkEnum(hkpConstraintInstanceOnDestructionRemapInfo, hkUint8)),
        Member(
            64,
            "listeners",
            hkpConstraintInstanceSmallArraySerializeOverrideType,
            MemberFlags.NotSerializable,
        ),
        Member(80, "name", hkStringPtr),
        Member(88, "userData", hkUlong),
        Member(96, "internal", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(104, "uid", hkUint32, MemberFlags.NotSerializable),
    )
    members = hkReferencedObject.members + local_members

    owner: hkReflectDetailOpaque
    data: hkpConstraintData
    constraintModifiers: hkpModifierConstraintAtom
    entities: tuple[hkpEntity]
    priority: hkpConstraintInstanceConstraintPriority
    wantRuntime: bool
    destructionRemapInfo: hkpConstraintInstanceOnDestructionRemapInfo
    listeners: hkpConstraintInstanceSmallArraySerializeOverrideType
    name: str
    userData: int
    internal: hkReflectDetailOpaque
    uid: int
