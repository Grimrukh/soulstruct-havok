from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *

from .hknpMaterial import hknpMaterial


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpMaterialLibrary(hkReferencedObject):
    alignment = 8
    byte_size = 72
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(24, "materialAddedSignal", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(32, "materialModifiedSignal", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(40, "materialRemovedSignal", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(48, "entries", hkFreeListArray(hknpMaterial, hkInt32), MemberFlags.Protected),
    )
    members = hkReferencedObject.members + local_members

    materialAddedSignal: None = None
    materialModifiedSignal: None = None
    materialRemovedSignal: None = None
    entries: list[hknpMaterial]
