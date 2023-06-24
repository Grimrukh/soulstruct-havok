from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkFreeListArrayhknpMaterialhknpMaterialId8hknpMaterialFreeListArrayOperations import hkFreeListArrayhknpMaterialhknpMaterialId8hknpMaterialFreeListArrayOperations


@dataclass(slots=True, eq=False, repr=False)
class hknpMaterialLibrary(hkReferencedObject):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "materialAddedSignal", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(24, "materialModifiedSignal", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(32, "materialRemovedSignal", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(40, "entries", hkFreeListArrayhknpMaterialhknpMaterialId8hknpMaterialFreeListArrayOperations),
    )
    members = hkReferencedObject.members + local_members

    materialAddedSignal: None
    materialModifiedSignal: None
    materialRemovedSignal: None
    entries: hkFreeListArrayhknpMaterialhknpMaterialId8hknpMaterialFreeListArrayOperations
