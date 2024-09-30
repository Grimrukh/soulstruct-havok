from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .._hkp.hkpRigidBody import hkpRigidBody
from .._hkp.hkpConstraintInstance import hkpConstraintInstance
from .hkaSkeleton import hkaSkeleton


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaRagdollInstance(hkReferencedObject):
    alignment = 8
    byte_size = 72
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2652690323

    local_members = (
        Member(16, "rigidBodies", hkArray(Ptr(hkpRigidBody, hsh=2417329070), hsh=1736666912)),
        Member(32, "constraints", hkArray(Ptr(hkpConstraintInstance, hsh=3107152142), hsh=3091539382)),
        Member(48, "boneToRigidBodyMap", hkArray(_int, hsh=2106159949)),
        Member(64, "skeleton", hkRefPtr(hkaSkeleton, hsh=1149764379)),
    )
    members = hkReferencedObject.members + local_members

    rigidBodies: list[hkpRigidBody]
    constraints: list[hkpConstraintInstance]
    boneToRigidBodyMap: list[int]
    skeleton: hkaSkeleton
