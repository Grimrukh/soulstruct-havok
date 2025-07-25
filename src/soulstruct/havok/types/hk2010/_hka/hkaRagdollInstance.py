from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .._hkp.hkpRigidBody import hkpRigidBody
from .._hkp.hkpConstraintInstance import hkpConstraintInstance
from .hkaSkeleton import hkaSkeleton


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaRagdollInstance(hkReferencedObject):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 357124328

    local_members = (
        Member(8, "rigidBodies", hkArray(Ptr(hkpRigidBody))),
        Member(20, "constraints", hkArray(Ptr(hkpConstraintInstance))),
        Member(32, "boneToRigidBodyMap", hkArray(hkInt32)),
        Member(44, "skeleton", Ptr(hkaSkeleton)),
    )
    members = hkReferencedObject.members + local_members

    rigidBodies: list[hkpRigidBody]
    constraints: list[hkpConstraintInstance]
    boneToRigidBodyMap: list[int]
    skeleton: hkaSkeleton
