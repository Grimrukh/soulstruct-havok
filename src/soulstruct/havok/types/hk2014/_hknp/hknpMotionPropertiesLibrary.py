from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from ..hkFreeListArrayhknpMotionPropertieshknpMotionPropertiesId8hknpMotionPropertiesFreeListArrayOperations import hkFreeListArrayhknpMotionPropertieshknpMotionPropertiesId8hknpMotionPropertiesFreeListArrayOperations


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpMotionPropertiesLibrary(hkReferencedObject):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "entryAddedSignal", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(24, "entryModifiedSignal", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(32, "entryRemovedSignal", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(
            40,
            "entries",
            hkFreeListArrayhknpMotionPropertieshknpMotionPropertiesId8hknpMotionPropertiesFreeListArrayOperations,
        ),
    )
    members = hkReferencedObject.members + local_members

    entryAddedSignal: None
    entryModifiedSignal: None
    entryRemovedSignal: None
    entries: hkFreeListArrayhknpMotionPropertieshknpMotionPropertiesId8hknpMotionPropertiesFreeListArrayOperations
