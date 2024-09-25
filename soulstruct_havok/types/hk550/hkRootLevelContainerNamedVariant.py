from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkRootLevelContainerNamedVariant(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(4, "className", hkStringPtr),
        # NOTE: In CPP, these two members are inside `hkVariant`, which is not serialized.
        Member(8, "variant", Ptr(hkReferencedObject)),  # `hkVariant.m_object`
        Member(12, "variantClass", Ptr(hkReflectDetailOpaque)),  # `hkVariant.m_class`
    )
    members = local_members

    name: str
    className: str
    variant: hkReferencedObject
    variantClass: None = None
