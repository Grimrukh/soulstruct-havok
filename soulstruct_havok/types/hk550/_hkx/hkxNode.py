from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkxAttributeHolder import hkxAttributeHolder


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxNode(hkxAttributeHolder):
    alignment = 16
    byte_size = 68
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(20, "name", hkStringPtr),
        Member(24, "object", Ptr(hkReferencedObject)),  # `hkVariant.m_object`
        Member(28, "keyFrames", Ptr(hkMatrix4)),
        Member(32, "numKeyFrames", hkInt32),
        Member(36, "children", hkArray(Ptr(DefType("hkxNode", lambda: hkxNode)))),  # recursive
        Member(48, "numChildren", hkInt32),
        Member(52, "annotations", Ptr(hkReflectDetailOpaque)),  # TODO: Ptr(hkxAnnotationData)),
        Member(56, "numAnnotations", hkInt32),
        Member(60, "userProperties", hkStringPtr),
        Member(64, "selected", hkBool),

    )
    members = hkxAttributeHolder.members + local_members

    name: str
    object: hkReferencedObject
    keyFrames: hkMatrix4
    numKeyFrames: int
    children: list[None]
    numChildren: int
    annotations: None = None
    numAnnotations: int
    userProperties: str
    selected: bool
