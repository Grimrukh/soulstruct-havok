from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkpRigidBody import hkpRigidBody
from .hkpConstraintInstance import hkpConstraintInstance
from .hkpAction import hkpAction
from .hkpPhantom import hkpPhantom


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpPhysicsSystem(hkReferencedObject):
    alignment = 16
    byte_size = 68
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 4285680663

    local_members = (
        Member(8, "rigidBodies", hkArray(Ptr(hkpRigidBody))),
        Member(20, "constraints", hkArray(Ptr(hkpConstraintInstance))),
        Member(32, "actions", hkArray(Ptr(hkpAction))),
        Member(44, "phantoms", hkArray(Ptr(hkpPhantom))),
        Member(56, "name", hkStringPtr),
        Member(60, "userData", hkUlong),
        Member(64, "active", hkBool),
    )
    members = hkReferencedObject.members + local_members

    rigidBodies: list[hkpRigidBody]
    constraints: list[hkpConstraintInstance]
    actions: list[hkpAction]
    phantoms: list[hkpPhantom]
    name: str
    userData: int
    active: bool
