from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hkpRigidBody import hkpRigidBody
from .hkpConstraintInstance import hkpConstraintInstance
from .hkpAction import hkpAction
from .hkpPhantom import hkpPhantom


class hkpPhysicsSystem(hkReferencedObject):
    alignment = 8
    byte_size = 104
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 4219313043

    local_members = (
        Member(
            16,
            "rigidBodies",
            hkArray(Ptr(hkpRigidBody, hsh=2417329070), hsh=1736666912),
            MemberFlags.Protected,
        ),
        Member(
            32,
            "constraints",
            hkArray(Ptr(hkpConstraintInstance, hsh=3107152142), hsh=3091539382),
            MemberFlags.Protected,
        ),
        Member(48, "actions", hkArray(Ptr(hkpAction)), MemberFlags.Protected),
        Member(64, "phantoms", hkArray(Ptr(hkpPhantom)), MemberFlags.Protected),
        Member(80, "name", hkStringPtr, MemberFlags.Protected),
        Member(88, "userData", hkUlong, MemberFlags.Protected),
        Member(96, "active", hkBool, MemberFlags.Protected),
    )
    members = hkReferencedObject.members + local_members

    rigidBodies: list[hkpRigidBody]
    constraints: list[hkpConstraintInstance]
    actions: list[hkpAction]
    phantoms: list[hkpPhantom]
    name: str
    userData: int
    active: bool
