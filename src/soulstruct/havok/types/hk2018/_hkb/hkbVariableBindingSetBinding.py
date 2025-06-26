from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkbVariableBindingSetBindingBindingType import hkbVariableBindingSetBindingBindingType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbVariableBindingSetBinding(hk):
    alignment = 8
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 135979325
    __version = 1
    __real_name = "hkbVariableBindingSet::Binding"

    local_members = (
        Member(0, "memberPath", hkStringPtr),
        Member(8, "memberType", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable | MemberFlags.Private),
        Member(16, "offsetInObjectPlusOne", hkInt32, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(20, "offsetInArrayPlusOne", hkInt32, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(24, "rootVariableIndex", hkInt32, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(28, "variableIndex", hkInt32),
        Member(32, "bitIndex", hkInt8),
        Member(33, "bindingType", hkEnum(hkbVariableBindingSetBindingBindingType, hkInt8)),
        Member(34, "variableType", hkInt8, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(35, "flags", hkFlags(hkInt8), MemberFlags.NotSerializable | MemberFlags.Private),
    )
    members = local_members

    memberPath: hkStringPtr
    memberType: hkReflectDetailOpaque
    offsetInObjectPlusOne: int
    offsetInArrayPlusOne: int
    rootVariableIndex: int
    variableIndex: int
    bitIndex: int
    bindingType: hkbVariableBindingSetBindingBindingType
    variableType: int
    flags: hkInt8
