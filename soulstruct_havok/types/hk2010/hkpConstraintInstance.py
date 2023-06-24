from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkpConstraintData import hkpConstraintData
from .hkpModifierConstraintAtom import hkpModifierConstraintAtom
from .hkpEntity import hkpEntity
from .hkpConstraintInstanceConstraintPriority import hkpConstraintInstanceConstraintPriority
from .hkpConstraintInstanceOnDestructionRemapInfo import hkpConstraintInstanceOnDestructionRemapInfo
from .hkpConstraintInstanceSmallArraySerializeOverrideType import hkpConstraintInstanceSmallArraySerializeOverrideType


@dataclass(slots=True, eq=False, repr=False)
class hkpConstraintInstance(hkReferencedObject):
    alignment = 16
    byte_size = 56
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 55491167

    local_members = (
        Member(8, "owner", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(12, "data", Ptr(hkpConstraintData)),
        Member(16, "constraintModifiers", Ptr(hkpModifierConstraintAtom)),
        Member(20, "entities", hkStruct(Ptr(hkpEntity), 2)),
        Member(28, "priority", hkEnum(hkpConstraintInstanceConstraintPriority, hkUint8)),
        Member(29, "wantRuntime", hkBool),
        Member(30, "destructionRemapInfo", hkEnum(hkpConstraintInstanceOnDestructionRemapInfo, hkUint8)),
        Member(
            32,
            "listeners",
            hkpConstraintInstanceSmallArraySerializeOverrideType,
            MemberFlags.NotSerializable,
        ),
        Member(40, "name", hkStringPtr),
        Member(44, "userData", hkUlong),
        Member(48, "internal", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(52, "uid", hkUint32, MemberFlags.NotSerializable),
    )
    members = hkReferencedObject.members + local_members

    owner: None
    data: hkpConstraintData
    constraintModifiers: hkpModifierConstraintAtom
    entities: tuple[hkpEntity, ...]
    priority: int
    wantRuntime: bool
    destructionRemapInfo: int
    listeners: hkpConstraintInstanceSmallArraySerializeOverrideType
    name: str
    userData: int
    internal: None
    uid: int
