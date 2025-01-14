from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkRootLevelContainerNamedVariant(hk):
    """NOTE: If type data is present in packfile, this will contain references to all variant types in that section."""
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2235206044

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(4, "className", hkStringPtr),
        # NOTE: In CPP, these two members are inside `hkVariant`, which is not serialized.
        Member(8, "variant", Ptr(hk)),  # `hkVariant.m_object`; does not need to be `hkReferencedObject`
        Member(12, "variantClass", Ptr(hkReflectDetailOpaque)),  # `hkVariant.m_class`
    )
    members = local_members

    name: str
    className: str
    variant: hk
    variantClass: None = None
