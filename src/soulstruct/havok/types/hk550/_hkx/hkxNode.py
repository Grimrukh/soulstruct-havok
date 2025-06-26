from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkxAttributeHolder import hkxAttributeHolder
from .hkxNodeAnnotationData import hkxNodeAnnotationData


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxNode(hkxAttributeHolder):
    alignment = 4
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 112139098

    local_members = (
        Member(8, "name", hkStringPtr),
        Member(12, "object", Ptr(hkReferencedObject)),  # `hkVariant.m_object`
        Member(16, "keyFrames", SimpleArray(hkMatrix4)),
        Member(24, "children", SimpleArray(Ptr(DefType("hkxNode", lambda: hkxNode)))),  # recursive
        Member(32, "annotations", SimpleArray(hkxNodeAnnotationData)),
        Member(40, "userProperties", hkStringPtr),
        Member(44, "selected", hkBool),

    )
    members = hkxAttributeHolder.members + local_members

    name: str
    object: hkReferencedObject
    keyFrames: hkMatrix4
    children: list[hkxNode]
    annotations: list[hkxNodeAnnotationData]
    userProperties: str
    selected: bool
